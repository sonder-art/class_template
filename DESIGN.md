Absolutely—here’s the **complete, merged, and expanded design doc** with **all schemas + RLS**, **ops**, **security/auth (BE+FE)**, and **fully specified API contracts with examples**. I also did a pass to tighten consistency, add missing pieces (like `/me`, rate limits, idempotency, example payloads), and note a few optimizations. This is the one canonical file to save.

---

# 0) Overview & Goals

* Multi-repo, multi-class setup powered by **Hugo (static)** + **Supabase** backend (Auth, SQL, Storage, RLS, Edge Functions).
* Each repo maps to a **class** (e.g., `class_template`). Pages are served at `{domain}/{repo}`.
* Users authenticate with **GitHub** via Supabase. Fine-grained access enforced by **RLS** and **Edge Functions**.
* Grading model: **Modules → Constituents → Items**. Students submit **Items** (with multiple parts). Professors grade, adjust, export.
* Design principles: **least privilege**, **stateless trust**, **idempotent APIs**, **non-destructive sync**, **auditable changes**.

---

# 1) Supabase Initialization

## 1.0 Conventions & prerequisites

* **Auth:** Supabase Auth (GitHub, PKCE on FE).
* **IDs:** `uuid` PKs; slugs unique in scope (per table where indicated).
* **Time:** `timestamptz` UTC; server enforces windows and lateness.
* **Storage:** private bucket `submissions`.
* **Part kinds:** `'file' | 'text' | 'url' | 'json'`.
* **Defaults:**

  * Module policy: `{"aggregator":"weighted_sum"}`
  * Constituent policy: `{"normalize_items":true}`
  * Item penalty: `{"late_allowed":false,"penalty_pct_per_day":0}`

**Auth provider (Supabase → Auth → Providers → GitHub):**

* Set callback URLs for prod and dev.
* Ensure **PKCE** is enabled (default with supabase-js v2).

**Edge Functions CORS (global):**

* Allow origins: `{your primary domain}`, any staging domains you use.
* Allow methods: `GET,POST,OPTIONS`.
* Allow headers: `Authorization,Content-Type`.

**Content-Security-Policy (served by GH Pages):**

* `default-src 'self'`
* `connect-src 'self' https://<project>.supabase.co https://<functions-domain>`
* Minimize `script-src`, set `frame-ancestors 'none'`.

---

## 1.1 People & tenancy

```sql
create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  github_username text,
  created_at timestamptz default now()
);

create table if not exists public.classes (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,                 -- e.g. "class_template"
  title text not null,
  github_repository_id bigint unique,
  github_repository_fullname text unique,    -- e.g. "your-org/class_template"
  enforcement_mode text default 'strict' check (enforcement_mode in ('strict','lenient')),
  created_at timestamptz default now()
);

create table if not exists public.class_professors (
  class_id uuid references public.classes(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  primary key (class_id, user_id)
);

create table if not exists public.class_students (
  class_id uuid references public.classes(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  enrolled_at timestamptz default now(),
  primary key (class_id, user_id)
);

create table if not exists public.class_enrollment_tokens (
  id bigserial primary key,
  class_id uuid references public.classes(id) on delete cascade,
  token_hash text not null,                  -- store only hash (bcrypt recommended)
  expires_at timestamptz not null,
  max_uses int default 0,                    -- 0 = unlimited within expiry
  uses int default 0,
  created_by uuid references auth.users(id),
  created_at timestamptz default now()
);

create table if not exists public.class_sites (
  class_id uuid references public.classes(id) on delete cascade,
  domain text not null,                      -- e.g. "https://yourdomain.com"
  base_path text not null,                   -- e.g. "/class_template"
  unique (domain, base_path)
);
```

**Safe test prompts**

```sql
insert into public.classes (slug,title,github_repository_id,github_repository_fullname)
values ('class_template','Class Template (Dev)',700000001,'your-org/class_template')
returning id;

insert into public.class_professors (class_id,user_id) values ('<class_id>','<prof_user_id>');
insert into public.class_students   (class_id,user_id) values ('<class_id>','<student_user_id>');

insert into public.class_sites (class_id,domain,base_path)
values ('<class_id>','https://yourdomain.com','/class_template');
```

---

## 1.2 Grading structure (Modules & Constituents)

```sql
create table if not exists public.class_structures (
  id uuid primary key default gen_random_uuid(),
  class_id uuid references public.classes(id) on delete cascade,
  version int not null,
  source_json jsonb not null,     -- modules + constituents only
  is_active boolean default true,
  created_at timestamptz default now(),
  unique (class_id, version)
);

create table if not exists public.modules (
  id uuid primary key default gen_random_uuid(),
  class_id uuid references public.classes(id) on delete cascade,
  slug text not null,
  title text not null,
  weight_over_100 numeric not null,           -- non-extra sum to 100
  policy jsonb default '{"aggregator":"weighted_sum"}'::jsonb,
  is_extra boolean default false,             -- extra module adds directly to final
  order_index int default 0,
  is_active boolean default true,
  unique (class_id, slug)
);

create table if not exists public.constituents (
  id uuid primary key default gen_random_uuid(),
  class_id uuid references public.classes(id) on delete cascade,
  module_id uuid references public.modules(id) on delete cascade,
  slug text not null,
  title text not null,
  weight_over_100 numeric not null,           -- non-extra sum to 100 per module
  policy jsonb default '{"normalize_items":true}'::jsonb,
  is_extra boolean default false,             -- optional module-level extra
  order_index int default 0,
  is_active boolean default true,
  unique (module_id, slug)
);
```

**Safe test prompts**

```sql
with cls as (select id from public.classes where slug='class_template')
insert into public.modules (class_id,slug,title,weight_over_100)
select id,'module_1','Module 1',50 from cls
union all select id,'module_2','Module 2',50 from cls
union all select id,'extra','Final Extra',0 from cls;

insert into public.constituents (class_id,module_id,slug,title,weight_over_100)
select m.class_id,m.id,'homeworks_1','Homeworks 1',70
from public.modules m where m.slug='module_1' and m.class_id=(select id from public.classes where slug='class_template');

insert into public.constituents (class_id,module_id,slug,title,weight_over_100)
select m.class_id,m.id,'exam_1','Exam 1',30
from public.modules m where m.slug='module_1' and m.class_id=(select id from public.classes where slug='class_template');

insert into public.constituents (class_id,module_id,slug,title,weight_over_100,is_extra)
select m.class_id,m.id,'extra','Extra (M1)',0,true
from public.modules m where m.slug='module_1' and m.class_id=(select id from public.classes where slug='class_template');
```

---

## 1.3 Items & Item Parts (uploadable unit)

```sql
create table if not exists public.items (
  id uuid primary key default gen_random_uuid(),
  class_id uuid not null references public.classes(id) on delete cascade,
  constituent_id uuid not null references public.constituents(id) on delete cascade,
  slug text not null,
  title text not null,
  max_points numeric not null,
  due_at timestamptz,
  deliver_policy jsonb default '{}'::jsonb,   -- opens_at, closes_at, grace_minutes...
  penalty jsonb default '{"late_allowed":false,"penalty_pct_per_day":0}'::jsonb,
  default_value numeric,
  default_policy jsonb default '{}'::jsonb,
  source jsonb default '{}'::jsonb,           -- e.g., page path, commit SHA
  order_index int default 0,
  is_active boolean default true,
  unique (constituent_id, slug)
);

create table if not exists public.item_parts (
  item_id uuid references public.items(id) on delete cascade,
  key text not null,
  kind text not null check (kind in ('file','text','url','json')),
  required boolean default true,
  validation jsonb default '{}'::jsonb,       -- max_bytes, mime, regex, maxLen...
  opens_at timestamptz,
  closes_at timestamptz,
  primary key (item_id, key)
);
```

**Safe test prompts**

```sql
with c as (
  select c.* from public.constituents c
  join public.modules m on m.id=c.module_id
  join public.classes cl on cl.id=m.class_id
  where cl.slug='class_template' and c.slug='homeworks_1'
)
insert into public.items (class_id,constituent_id,slug,title,max_points,due_at,default_value)
select c.class_id,c.id,'hw1','Homework 1',50,'2025-09-14T23:59:00Z'::timestamptz,0 from c
returning id;

insert into public.item_parts (item_id,key,kind,validation)
values ('<item_id>','code','file','{"max_bytes":5242880,"mime":["application/zip","text/plain"]}'),
       ('<item_id>','writeup','text','{"maxLen":8000}');
```

---

## 1.4 Submissions & history

```sql
create table if not exists public.submissions (
  item_id uuid references public.items(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  part_key text not null,

  storage_path text,                           -- if kind='file'
  text_payload text,                           -- if kind='text'
  url_payload text,                            -- if kind='url'
  json_payload jsonb,                          -- if kind='json'

  submitted_at timestamptz default now(),
  version int default 1,
  size_bytes int,
  content_type text,
  etag text,
  sha256 text,
  client_ip inet,
  user_agent text,
  source text,                                  -- "web" | "api" | "action"
  lateness_minutes int default 0,

  primary key (item_id, user_id, part_key)
);

create table if not exists public.submissions_history (
  id bigserial primary key,
  item_id uuid not null,
  user_id uuid not null,
  part_key text not null,
  action text not null check (action in ('insert','update','delete')),
  at timestamptz default now(),
  actor_user_id uuid not null,
  old_row jsonb,
  new_row jsonb
);

create or replace function public.log_submissions_history()
returns trigger language plpgsql as $$
begin
  if (tg_op = 'INSERT') then
    insert into public.submissions_history(item_id,user_id,part_key,action,actor_user_id,old_row,new_row)
    values (new.item_id,new.user_id,new.part_key,'insert',auth.uid(),null,row_to_json(new));
    return new;
  elsif (tg_op = 'UPDATE') then
    new.version := coalesce(old.version,1) + 1;
    insert into public.submissions_history(item_id,user_id,part_key,action,actor_user_id,old_row,new_row)
    values (new.item_id,new.user_id,new.part_key,'update',auth.uid(),row_to_json(old),row_to_json(new));
    return new;
  elsif (tg_op = 'DELETE') then
    insert into public.submissions_history(item_id,user_id,part_key,action,actor_user_id,old_row,new_row)
    values (old.item_id,old.user_id,old.part_key,'delete',auth.uid(),row_to_json(old),null);
    return old;
  end if;
end $$;

drop trigger if exists t_submissions_hist on public.submissions;
create trigger t_submissions_hist
after insert or update or delete on public.submissions
for each row execute procedure public.log_submissions_history();
```

---

## 1.5 Item grades, adjustments & grade history

```sql
create table if not exists public.item_grades (
  item_id uuid references public.items(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  points_earned numeric not null,
  max_points_override numeric,
  graded_at timestamptz default now(),
  grader_id uuid references auth.users(id),
  source text default 'manual',
  primary key (item_id, user_id)
);

create table if not exists public.item_grades_history (
  id bigserial primary key,
  item_id uuid not null,
  user_id uuid not null,
  at timestamptz default now(),
  actor_user_id uuid not null,
  old_row jsonb,
  new_row jsonb
);

create or replace function public.log_item_grades_history()
returns trigger language plpgsql as $$
begin
  if (tg_op = 'INSERT') then
    insert into public.item_grades_history(item_id,user_id,actor_user_id,old_row,new_row)
    values (new.item_id,new.user_id,auth.uid(),null,row_to_json(new));
    return new;
  elsif (tg_op = 'UPDATE') then
    insert into public.item_grades_history(item_id,user_id,actor_user_id,old_row,new_row)
    values (new.item_id,new.user_id,auth.uid(),row_to_json(old),row_to_json(new));
    return new;
  elsif (tg_op = 'DELETE') then
    insert into public.item_grades_history(item_id,user_id,actor_user_id,old_row,new_row)
    values (old.item_id,old.user_id,auth.uid(),row_to_json(old),null);
    return old;
  end if;
end $$;

drop trigger if exists t_item_grades_hist on public.item_grades;
create trigger t_item_grades_hist
after insert or update or delete on public.item_grades
for each row execute procedure public.log_item_grades_history();

create table if not exists public.constituent_adjustments (
  constituent_id uuid references public.constituents(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  delta_points numeric not null default 0,
  note text,
  updated_at timestamptz default now(),
  updated_by uuid references auth.users(id),
  primary key (constituent_id, user_id)
);

create table if not exists public.module_adjustments (
  class_id uuid references public.classes(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  delta_points numeric not null default 0,     -- direct to final
  note text,
  updated_at timestamptz default now(),
  updated_by uuid references auth.users(id),
  primary key (class_id, user_id)
);
```

---

## 1.6 Policy registry (named logic)

```sql
create table if not exists public.policy_registry (
  id uuid primary key default gen_random_uuid(),
  scope text not null check (scope in ('module','constituent','item')),
  name text not null,
  sql_function text not null,
  description text,
  params_json_schema jsonb default '{}'::jsonb,
  is_active boolean default true,
  unique (scope, name)
);

create table if not exists public.policy_bindings (
  id uuid primary key default gen_random_uuid(),
  scope text not null check (scope in ('module','constituent','item')),
  target_id uuid not null,      -- modules.id / constituents.id / items.id
  policy_name text not null,
  params jsonb default '{}'::jsonb,
  unique (scope, target_id)
);

insert into public.policy_registry (scope,name,sql_function,description) values
('module','weighted_sum','grade_agg_weighted_sum','Default weighted sum within module'),
('module','leontief_min','grade_agg_leontief_min','Leontief (min) across constituents'),
('item','late_linear','grade_apply_item_penalty_late_linear','Linear late penalty on items')
on conflict do nothing;
```

**Example SQL function (optional starter)**

```sql
-- Simple Leontief min: module score = min(constituent_total_percent)
create or replace function grade_agg_leontief_min(module_uuid uuid, user_uuid uuid)
returns numeric language sql stable as $$
  select coalesce(min(constituent_total_percent),0)
  from public.v_constituent_totals
  where module_id = module_uuid and user_id = user_uuid;
$$;
```

---

## 1.7 Computed views (live grades; include all students)

```sql
create or replace view public.v_item_last_submission as
select item_id, user_id, max(submitted_at) as last_submitted_at
from public.submissions group by item_id, user_id;

create or replace view public.v_item_scores as
select
  i.class_id,
  i.constituent_id,
  i.id as item_id,
  cs.user_id,
  coalesce(g.points_earned, i.default_value, 0) as points_earned_effective,
  coalesce(g.max_points_override, i.max_points) as max_points
from public.items i
join public.constituents c on c.id = i.constituent_id and c.is_active
join public.modules m on m.id = c.module_id and m.is_active
join public.class_students cs on cs.class_id = m.class_id
left join public.item_grades g on g.item_id = i.id and g.user_id = cs.user_id
where i.is_active = true;

create or replace view public.v_constituent_scores as
with sums as (
  select class_id, constituent_id, user_id,
         sum(points_earned_effective) as earned,
         nullif(sum(max_points),0) as max_sum
  from public.v_item_scores
  group by 1,2,3
)
select
  c.class_id, c.module_id, c.id as constituent_id, s.user_id,
  case when s.max_sum is null then 0 else (s.earned / s.max_sum) * 100 end as constituent_raw_percent
from sums s
join public.constituents c on c.id = s.constituent_id and c.is_active = true;

create or replace view public.v_constituent_totals as
select
  cs.class_id, cs.module_id, cs.constituent_id, cs.user_id,
  cs.constituent_raw_percent + coalesce(ca.delta_points,0) as constituent_total_percent,
  c.is_extra, c.weight_over_100 as cons_weight
from public.v_constituent_scores cs
join public.constituents c on c.id = cs.constituent_id
left join public.constituent_adjustments ca
  on ca.constituent_id = cs.constituent_id and ca.user_id = cs.user_id;

create or replace view public.v_module_totals as
with weighted as (
  select
    ct.class_id, ct.module_id, ct.user_id,
    case when ct.is_extra then 0 else ct.constituent_total_percent * (ct.cons_weight/100.0) end as weighted_percent,
    case when ct.is_extra then ct.constituent_total_percent else 0 end as extra_add
  from public.v_constituent_totals ct
)
select
  m.class_id, m.id as module_id, w.user_id,
  coalesce(sum(w.weighted_percent),0) as module_sum_percent,
  coalesce(sum(w.extra_add),0) as module_extra_percent,
  m.weight_over_100 as module_weight,
  m.is_extra,
  m.policy
from public.modules m
left join weighted w on w.module_id = m.id
where m.is_active = true
group by m.class_id, m.id, w.user_id, m.weight_over_100, m.is_extra, m.policy;

create or replace view public.v_module_contributions as
select
  class_id, module_id, user_id,
  case when is_extra then 0 else (module_sum_percent/100.0) * module_weight end as contribution_points,
  case when is_extra then (module_sum_percent + module_extra_percent) else 0 end as extra_module_points
from public.v_module_totals;

create or replace view public.v_final_grades as
select
  cs.class_id, cs.user_id,
  coalesce(sum(mc.contribution_points),0) as weighted_points,
  coalesce(sum(mc.extra_module_points),0) as extra_module_points,
  coalesce(ma.delta_points, 0) as final_adjustment_points,
  coalesce(sum(mc.contribution_points),0) + coalesce(sum(mc.extra_module_points),0) + coalesce(ma.delta_points,0) as final_points
from public.class_students cs
left join public.v_module_contributions mc
  on mc.class_id = cs.class_id and mc.user_id = cs.user_id
left join public.module_adjustments ma
  on ma.class_id = cs.class_id and ma.user_id = cs.user_id
group by cs.class_id, cs.user_id, ma.delta_points;
```

---

## 1.8 RLS policies (enable after seeding)

```sql
-- enable RLS on all tables above (not repeated here for brevity)

-- PUBLIC READ
create policy classes_read on public.classes for select using (true);

-- membership self-read
create policy profs_self_read    on public.class_professors for select using (auth.uid() = user_id);
create policy students_self_read on public.class_students   for select using (auth.uid() = user_id);

-- structures readable to members
create policy structures_read_members on public.class_structures
for select using (
  exists(select 1 from public.class_students   cs where cs.class_id = class_structures.class_id and cs.user_id = auth.uid())
  or exists(select 1 from public.class_professors cp where cp.class_id = class_structures.class_id and cp.user_id = auth.uid())
);

create policy modules_read_members on public.modules
for select using (
  exists(select 1 from public.class_students   cs where cs.class_id = modules.class_id and cs.user_id = auth.uid())
  or exists(select 1 from public.class_professors cp where cp.class_id = modules.class_id and cp.user_id = auth.uid())
);

create policy constituents_read_members on public.constituents
for select using (
  exists(select 1 from public.modules m
           join public.class_students   cs on cs.class_id = m.class_id and cs.user_id = auth.uid()
           where m.id = constituents.module_id)
  or exists(select 1 from public.modules m
           join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
           where m.id = constituents.module_id)
);

create policy items_read_members on public.items
for select using (
  exists(select 1 from public.constituents c
           join public.modules m on m.id = c.module_id
           join public.class_students   cs on cs.class_id = m.class_id and cs.user_id = auth.uid()
           where c.id = items.constituent_id)
  or exists(select 1 from public.constituents c
           join public.modules m on m.id = c.module_id
           join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
           where c.id = items.constituent_id)
);

create policy item_parts_read_members on public.item_parts
for select using (
  exists(select 1 from public.items i
           join public.constituents c on c.id = i.constituent_id
           join public.modules m on m.id = c.module_id
           join public.class_students   cs on cs.class_id = m.class_id and cs.user_id = auth.uid()
           where i.id = item_parts.item_id)
  or exists(select 1 from public.items i
           join public.constituents c on c.id = i.constituent_id
           join public.modules m on m.id = c.module_id
           join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
           where i.id = item_parts.item_id)
);

-- submissions
create policy submissions_select_student on public.submissions for select using (user_id = auth.uid());
create policy submissions_select_prof    on public.submissions for select using (
  exists (select 1 from public.items i
          join public.constituents c on c.id = i.constituent_id
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where i.id = submissions.item_id)
);
create policy submissions_write_student on public.submissions
for insert with check (user_id = auth.uid()),
    update using (user_id = auth.uid())
    with check (user_id = auth.uid());

-- submissions history: professor-only
create policy submissions_history_prof_read on public.submissions_history
for select using (
  exists (select 1 from public.items i
          join public.constituents c on c.id = i.constituent_id
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where i.id = submissions_history.item_id)
);

-- item grades: students self-read; professors RW for their class
create policy item_grades_student_self_read on public.item_grades for select using (user_id = auth.uid());

create policy item_grades_prof_rw on public.item_grades
for select using (
  exists (select 1 from public.items i
          join public.constituents c on c.id = i.constituent_id
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where i.id = item_grades.item_id)
)
, insert with check (
  exists (select 1 from public.items i
          join public.constituents c on c.id = i.constituent_id
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where i.id = item_grades.item_id)
)
, update using (
  exists (select 1 from public.items i
          join public.constituents c on c.id = i.constituent_id
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where i.id = item_grades.item_id)
);

-- item grades history: professor-only
create policy item_grades_history_prof_read on public.item_grades_history
for select using (
  exists (select 1 from public.items i
          join public.constituents c on c.id = i.constituent_id
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where i.id = item_grades_history.item_id)
);

-- adjustments
create policy adjustments_prof_rw_constituent on public.constituent_adjustments
for select using (
  exists (select 1 from public.constituents c
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where c.id = constituent_adjustments.constituent_id)
)
, insert with check (exists (select 1 from public.constituents c
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where c.id = constituent_adjustments.constituent_id))
, update using (exists (select 1 from public.constituents c
          join public.modules m on m.id = c.module_id
          join public.class_professors cp on cp.class_id = m.class_id and cp.user_id = auth.uid()
          where c.id = constituent_adjustments.constituent_id));

create policy adjustments_prof_rw_module on public.module_adjustments
for select using (exists (select 1 from public.class_professors cp where cp.class_id = module_adjustments.class_id and cp.user_id = auth.uid()))
, insert with check (exists (select 1 from public.class_professors cp where cp.class_id = module_adjustments.class_id and cp.user_id = auth.uid()))
, update using (exists (select 1 from public.class_professors cp where cp.class_id = module_adjustments.class_id and cp.user_id = auth.uid()));

-- policy registry/bindings: professor-read
create policy policy_registry_prof_read on public.policy_registry for select using (
  exists (select 1 from public.class_professors where user_id = auth.uid())
);
create policy policy_bindings_prof_read on public.policy_bindings for select using (
  exists (select 1 from public.class_professors where user_id = auth.uid())
);
```

---

## 1.9 Storage bucket

* Create **private** bucket `submissions`.
* Path: `class/<class_id>/item/<item_id>/user/<user_id>/<part_key>`.
* Recommended: **5-minute** presigned URLs, single-purpose (PUT vs GET).

---

## 1.10 Indexes

```sql
create index if not exists idx_modules_class          on public.modules(class_id);
create index if not exists idx_constituents_module    on public.constituents(module_id);
create index if not exists idx_constituents_class     on public.constituents(class_id);
create index if not exists idx_items_constituent      on public.items(constituent_id);
create index if not exists idx_items_class            on public.items(class_id);
create index if not exists idx_item_parts_item        on public.item_parts(item_id);

create index if not exists idx_submissions_item_user  on public.submissions(item_id, user_id);
create index if not exists idx_submissions_user       on public.submissions(user_id);

create index if not exists idx_item_grades_item_user  on public.item_grades(item_id, user_id);
create index if not exists idx_item_grades_user       on public.item_grades(user_id);
```

---

## 1.11 Consistency triggers

```sql
create or replace function public.enforce_constituent_class()
returns trigger language plpgsql as $$
declare mod_class uuid;
begin
  select class_id into mod_class from public.modules where id = new.module_id;
  new.class_id := mod_class;
  return new;
end $$;

drop trigger if exists t_constituents_class on public.constituents;
create trigger t_constituents_class
before insert or update on public.constituents
for each row execute procedure public.enforce_constituent_class();

create or replace function public.enforce_item_class()
returns trigger language plpgsql as $$
declare cons_class uuid;
begin
  select class_id into cons_class from public.constituents where id = new.constituent_id;
  new.class_id := cons_class;
  return new;
end $$;

drop trigger if exists t_items_class on public.items;
create trigger t_items_class
before insert or update on public.items
for each row execute procedure public.enforce_item_class();
```

---

# 2) Supabase Direct Prompts (regular ops)

## 2.1 Enrollment tokens

```sql
insert into public.class_enrollment_tokens (class_id, token_hash, expires_at, max_uses, created_by)
values ('<class_id>', crypt('<PLAINTEXT_TOKEN>', gen_salt('bf')), now() + interval '1 day', 0, '<prof_user_id>');
```

## 2.2 Integrity checks

```sql
-- modules sum check
with t as (
  select class_id, sum(weight_over_100) s from public.modules
  where is_active and is_extra=false group by class_id
) select * from t where s <> 100;

-- constituents sum check
with t as (
  select module_id, sum(weight_over_100) s from public.constituents
  where is_active and is_extra=false group by module_id
)
select t.*, m.slug module_slug from t
join public.modules m on m.id=t.module_id
where s <> 100;

-- duplicate class slugs sanity check
select slug, count(*) c, array_agg(github_repository_fullname)
from public.classes group by slug having count(*)>1;
```

## 2.3 Deactivation (non-destructive)

```sql
update public.items        set is_active=false where id='<item_id>';
update public.constituents set is_active=false where id='<constituent_id>';
update public.modules      set is_active=false where id='<module_id>';
```

## 2.4 Admin Exports (optional)

```sql
-- Final grades export
select pr.github_username, fg.*
from public.v_final_grades fg
left join public.profiles pr on pr.user_id = fg.user_id
where fg.class_id = '<class_id>'
order by pr.github_username;

-- Per-item submissions export (prof/admin)
select pr.github_username, s.*
from public.submissions s
left join public.profiles pr on pr.user_id=s.user_id
where s.item_id = '<item_id>'
order by pr.github_username, s.part_key;
```

---

# 3) Security & Auth Model (BE + FE)

## 3.1 Principles

* **Least privilege**: clients use anon key; RLS & Edge checks enforce access.
* **Stateless trust**: recompute class membership on every request.
* **No client authority**: UI gates are hints; server is authoritative.
* **Short-lived URLs**: all Storage access via short presigned URLs.

## 3.2 Identity & Sessions

* **Login:** GitHub OAuth via Supabase (PKCE).
* **Session:** `supabase-js` manages access/refresh tokens (`persistSession: true`).
* **Requests:** FE always sends `Authorization: Bearer <access_token>` to PostgREST and Edge Functions.

## 3.3 Edge Function authorization toolkit (use everywhere)

* `getUserOr401(req)` → verify token, return `{ user_id }`.
* `resolveClassOr404(class_slug)` → `{ class_id }`.
* `requireMembership(class_id, user_id, 'professor'|'student'|'member')`.
* `supabaseForUser(req)` → RLS-aware client using caller JWT.
* `withServiceRole()` → use only after checks, for Storage signing or admin tasks.
* Helpers: `getItemBySlug`, `getConstituentBySlug`, `checkTimeWindows`.
* **Rate-limit** per user/IP on sensitive endpoints (upload URL minting, text submit).

## 3.4 Database helpers

```sql
create or replace function is_professor_of(class_id uuid, uid uuid) returns boolean
language sql stable as $$ select exists(select 1 from class_professors where class_id=$1 and user_id=$2) $$;

create or replace function is_student_of(class_id uuid, uid uuid) returns boolean
language sql stable as $$ select exists(select 1 from class_students where class_id=$1 and user_id=$2) $$;
```

## 3.5 Storage security

* **Bucket** private; **no direct public URLs**.
* Upload = get signed PUT → PUT file → confirm. Download = get signed GET. Both gated by membership/time.

## 3.6 CI sync security

* `/sync-structure` & `/sync-items` accept **GitHub OIDC** only; validate `repository_id` matches class.

## 3.7 Frontend session & auth flow (static site)

1. Init `supabase-js` (`persistSession: true`, `autoRefreshToken: true`).
2. On load, if no session → show “Sign in with GitHub”.
3. After sign-in, call `/me?class_slug=...` to get `{ user_id, class_id, is_professor, is_student }`.
4. Gate UI with those flags (server still re-checks).
5. All requests include `class_slug`, plus `item_slug` when relevant.
6. Handle `401/403` centrally (re-login / not-enrolled).

---

# 4) Front End Contracts (Edge Functions) — **Detailed API Specs & Examples**

> Headers for all FE calls:
> `Authorization: Bearer <supabase access token>`
> `Content-Type: application/json`

## 4.0 Common error shape

```json
{ "error": { "code": "forbidden", "message": "Professor role required" } }
```

**Possible `code`:** `unauthorized`, `forbidden`, `not_found`, `invalid_input`, `window_closed`, `conflict`, `rate_limited`, `internal`.

---

## 4.1 Identity & bootstrap

### GET `/me`

* **Auth:** required (student/professor).
* **Purpose:** Resolve membership context for FE after login.
* **Query:** `?class_slug=class_template`
* **Security:** `getUserOr401` → `resolveClassOr404` → return membership booleans.
* **Response (200):**

```json
{
  "user_id": "e0f1-...",
  "class_id": "a1b2-...",
  "is_professor": false,
  "is_student": true
}
```

**Example request**

```
GET /me?class_slug=class_template
Authorization: Bearer <token>
```

---

## 4.2 Enrollment

### POST `/enroll-in-class`

* **Auth:** required (logged-in GitHub user).
* **Body:**

```json
{ "class_slug": "class_template", "token": "<plaintext-enrollment-token>" }
```

* **Checks:** class exists, token valid/not expired/usage-cap, not already enrolled.
* **Idempotent:** yes (second call returns same success).
* **Response (200):** `{ "ok": true, "class_id": "<uuid>" }`
* **Errors:** `invalid_token`, `expired_token`, `conflict` (already enrolled).

**Example**

```http
POST /enroll-in-class
Authorization: Bearer <token>
Content-Type: application/json

{ "class_slug": "class_template", "token": "ABC-DEF-123" }
```

---

## 4.3 CI sync (non-destructive, idempotent)

### POST `/sync-structure`

* **Auth:** **GitHub OIDC only** (CI).
* **Body (example):**

```json
{
  "class_slug": "class_template",
  "version": 2,
  "modules": [
    { "slug": "module_1", "title": "Module 1", "weight_over_100": 50,
      "policy": {"aggregator":"weighted_sum"},
      "constituents": [
        { "slug":"homeworks_1","title":"Homeworks 1","weight_over_100":70 },
        { "slug":"exam_1","title":"Exam 1","weight_over_100":30 },
        { "slug":"extra","title":"Extra (M1)","weight_over_100":0,"is_extra":true }
      ]
    },
    { "slug":"module_2", "title":"Module 2", "weight_over_100":50 },
    { "slug":"extra", "title":"Final Extra", "weight_over_100":0, "is_extra":true }
  ],
  "dry_run": false
}
```

* **Checks:** repository\_id matches class; module/constituent weights sum; version monotonic (optional strictness).
* **Response (200):**

```json
{
  "upserted": { "modules": 3, "constituents": 3 },
  "deactivated": { "modules": 0, "constituents": 0 },
  "warnings": [],
  "version": 2
}
```

### POST `/sync-items`

* **Auth:** GitHub OIDC only (CI).
* **Body (example):**

```json
{
  "class_slug": "class_template",
  "items": [
    {
      "slug": "hw1",
      "title": "Homework 1",
      "constituent_slug": "homeworks_1",
      "max_points": 50,
      "due_at": "2025-09-14T23:59:00Z",
      "deliver_policy": { "opens_at":"2025-09-01T00:00:00Z", "closes_at":"2025-09-14T23:59:00Z", "grace_minutes":0 },
      "penalty": { "late_allowed": false, "penalty_pct_per_day": 0 },
      "default_value": 0,
      "default_policy": {},
      "parts": [
        { "key":"code","kind":"file","required":true,"validation":{"max_bytes":5242880,"mime":["application/zip","text/plain"]}},
        { "key":"writeup","kind":"text","required":true,"validation":{"maxLen":8000}}
      ],
      "source": { "page": "/content/hw1.md", "commit": "abc123" }
    }
  ],
  "dry_run": false
}
```

* **Response (200):**

```json
{ "upserted_items": 1, "upserted_parts": 2, "deactivated": { "items": 0, "parts": 0 }, "warnings": [] }
```

---

## 4.4 Submissions (students)

### POST `/get-upload-url-item`

* **Auth:** student.
* **Rate limit:** e.g., 30/min per user + 120/min per IP.
* **Body:**

```json
{ "class_slug":"class_template", "item_slug":"hw1", "part_key":"code", "content_type":"application/zip", "size_bytes": 123456 }
```

* **Checks:** member (student), part kind=`file`, time windows open, validation (size/mime).
* **Response (200):**

```json
{
  "url":"https://...signed-put",
  "path":"class/<class_id>/item/<item_id>/user/<user_id>/code",
  "expires_in":300,
  "nonce":"b0f1..."  // optional if you implement single-use enforcement
}
```

### POST `/confirm-upload-item`

* **Auth:** student.
* **Idempotent:** yes (increments version each time).
* **Body:**

```json
{ "class_slug":"class_template", "item_slug":"hw1", "part_key":"code", "path":"class/.../code", "sha256":"...", "etag":"...", "nonce":"b0f1..." }
```

* **Checks:** path matches canonical; optional nonce; compute `lateness_minutes` vs due/grace.
* **Response (200):**

```json
{ "ok": true, "version": 3, "submitted_at": "2025-09-10T18:15:00Z", "lateness_minutes": 0 }
```

### POST `/submit-item-text`

* **Auth:** student.
* **Body:**

```json
{ "class_slug":"class_template", "item_slug":"hw1", "part_key":"writeup", "value":"This is my answer..." }
```

* **Checks:** part kind=`text`, validate `maxLen`; time window; upsert `submissions`.
* **Response:** `{ "ok": true, "version": 2, "submitted_at": "..." }`

*(Similarly `/submit-item-url` and `/submit-item-json` with `"value":"https://..."` or JSON value.)*

### GET `/get-download-url-item`

* **Auth:** student (self) or professor (class).
* **Query:**

```
?class_slug=class_template&item_slug=hw1&part_key=code&user_id=<optional>
```

* **Response (200):**

```json
{ "url":"https://...signed-get", "expires_in":300 }
```

---

## 4.5 Grades & adjustments (professors)

### POST `/upsert-item-grade`

* **Auth:** professor.
* **Body:**

```json
{ "class_slug":"class_template", "item_slug":"hw1", "user_id":"<uuid>", "points_earned": 42, "max_points_override": null }
```

* **Response:** `{ "ok": true }`
* **Side effects:** writes `item_grades` (upsert), logs `item_grades_history`.

### POST `/adjust-constituent`

```json
{ "class_slug":"class_template", "constituent_slug":"homeworks_1", "user_id":"<uuid>", "delta_points": 5, "note": "bonus" }
```

### POST `/adjust-final`

```json
{ "class_slug":"class_template", "user_id":"<uuid>", "delta_points": 2, "note": "participation" }
```

---

## 4.6 Student read APIs (current status)

### GET `/my/grade`

* **Returns:** the single row from `v_final_grades` for caller.
* **Example 200:**

```json
{ "class_id":"...","user_id":"...","weighted_points":83.2,"extra_module_points":1.5,"final_adjustment_points":2,"final_points":86.7 }
```

### GET `/my/grades/modules`

* **Returns:** module contributions for caller.
* **Example 200:**

```json
[
  { "module_slug":"module_1","module_sum_percent":92.0,"module_weight":50,"is_extra":false,"contribution_points":46.0 },
  { "module_slug":"extra","module_sum_percent":5.0,"module_weight":0,"is_extra":true,"contribution_points":0.0 }
]
```

### GET `/my/grades/constituents`

* **Returns:** constituent totals for caller.

```json
[
  { "module_slug":"module_1","constituent_slug":"homeworks_1","total_percent":95.0,"cons_weight":70,"is_extra":false },
  { "module_slug":"module_1","constituent_slug":"exam_1","total_percent":85.0,"cons_weight":30,"is_extra":false },
  { "module_slug":"module_1","constituent_slug":"extra","total_percent":5.0,"is_extra":true }
]
```

### GET `/my/grades/items`

* **Returns:** per-item points for caller.

```json
[
  { "constituent_slug":"homeworks_1","item_slug":"hw1","title":"Homework 1","points_earned_effective":42,"max_points":50 }
]
```

### GET `/my/items/status`

* **Returns:** for each item & part: required? submitted? timestamps, lateness, due/open/close.

```json
[
  {
    "item_slug":"hw1","title":"Homework 1","due_at":"2025-09-14T23:59:00Z",
    "parts":[
      {"part_key":"code","kind":"file","required":true,"submitted":true,"version":3,"submitted_at":"2025-09-10T18:15:00Z","lateness_minutes":0,"opens_at":"2025-09-01T00:00:00Z","closes_at":"2025-09-14T23:59:00Z"},
      {"part_key":"writeup","kind":"text","required":true,"submitted":false,"version":null,"submitted_at":null,"lateness_minutes":null,"opens_at":"2025-09-01T00:00:00Z","closes_at":"2025-09-14T23:59:00Z"}
    ]
  }
]
```

### GET `/my/items/missing`

```json
[
  { "item_slug":"hw1","part_key":"writeup","required":true }
]
```

### GET `/my/items/upcoming?days=14`

```json
[
  { "item_slug":"hw2","title":"Homework 2","due_at":"2025-09-20T23:59:00Z","opens_at":"2025-09-10T00:00:00Z","closes_at":"2025-09-20T23:59:00Z" }
]
```

### GET `/my/items/detail?item_slug=hw1`

```json
{
  "item": { "slug":"hw1","title":"Homework 1","max_points":50,"due_at":"2025-09-14T23:59:00Z" },
  "parts": [
    {"part_key":"code","kind":"file","required":true,"validation":{"max_bytes":5242880,"mime":["application/zip","text/plain"]}},
    {"part_key":"writeup","kind":"text","required":true,"validation":{"maxLen":8000}}
  ],
  "my_submissions": [
    {"part_key":"code","version":3,"submitted_at":"2025-09-10T18:15:00Z","lateness_minutes":0},
    {"part_key":"writeup","version":null,"submitted_at":null}
  ],
  "my_grade": { "points_earned":42, "max_points":50 }
}
```

---

## 4.7 Professor read APIs

### GET `/class/items/{item_slug}/submissions`

* **Auth:** professor.
* **Response 200:**

```json
[
  { "user_id":"...","github_username":"alice","part_key":"code","submitted_at":"...","version":2,"lateness_minutes":0 },
  { "user_id":"...","github_username":"alice","part_key":"writeup","submitted_at":"...","version":1,"lateness_minutes":0 }
]
```

### GET `/grade-breakdown?class_slug=class_template&user_id=<uuid>`

```json
{
  "final": { "weighted_points":83.2,"extra_module_points":1.5,"final_adjustment_points":2,"final_points":86.7 },
  "modules": [
    {
      "slug":"module_1","title":"Module 1","weight_over_100":50,
      "sum_percent":92.0,"extra_percent":5.0,"contribution_points":46.0,"is_extra":false,
      "constituents":[
        {"slug":"homeworks_1","title":"Homeworks 1","weight_over_100":70,"total_percent":95.0},
        {"slug":"exam_1","title":"Exam 1","weight_over_100":30,"total_percent":85.0},
        {"slug":"extra","title":"Extra (M1)","is_extra":true,"total_percent":5.0}
      ]
    }
  ]
}
```

### GET `/export-grades?class_slug=class_template&format=csv`

* **Auth:** professor.
* **Returns:** file stream (CSV) or JSON array.

---

## 4.8 Endpoint notes (security, idempotency, RLS, pagination)

* **Idempotency keys:** For write endpoints that could be retried (e.g., `confirm-upload-item`), you *may* accept `Idempotency-Key` header and record it in a small table keyed by `(user_id, endpoint, key)` to return prior result.
* **Pagination:** For collection GETs (submissions, items), support `limit` (<=100), `cursor` (opaque).
* **RLS vs service role:** Prefer **RLS client** (`supabaseForUser`) for reads/writes; use **service role** only to **sign Storage URLs** after authorization checks.
* **Rate limits:** return `429` with `Retry-After` where applicable.

---

# 5) Edge Function Implementation Skeletons (pseudo-code)

### `get-upload-url-item`

```ts
const user = getUserOr401(req);
const { class_slug, item_slug, part_key, content_type, size_bytes } = parseBody(req);
const { class_id } = resolveClassOr404(class_slug);
requireMembership(class_id, user.id, 'student');

const sb = supabaseForUser(req); // RLS client
const item = await getItemBySlug(sb, class_id, item_slug);
const part = await getPart(sb, item.id, part_key);
assert(part.kind === 'file');
assert(validateContent(part.validation, content_type, size_bytes));

assert(timeWindowOpen(item, part)); // server clock

const path = canonicalPath(class_id, item.id, user.id, part_key);
const url = await withServiceRole().storage.from('submissions').createSignedUploadUrl(path, { contentType: content_type, expiresIn: 300 });
return json({ url, path, expires_in: 300 });
```

### `confirm-upload-item`

```ts
const user = getUserOr401(req);
const { class_slug, item_slug, part_key, path, sha256, etag } = parseBody(req);
const { class_id } = resolveClassOr404(class_slug);
requireMembership(class_id, user.id, 'student');

const sb = supabaseForUser(req);
const item = await getItemBySlug(sb, class_id, item_slug);
const expected = canonicalPath(class_id, item.id, user.id, part_key);
assert(path === expected);

const lateness = computeLateness(item); // server time vs due/grace
await sb.from('submissions').upsert({
  item_id: item.id, user_id: user.id, part_key,
  storage_path: path, etag, sha256, submitted_at: new Date().toISOString(), lateness_minutes: lateness, source: 'web'
});
return json({ ok: true, version: /* read back version */, submitted_at: /* now */, lateness_minutes: lateness });
```

### `upsert-item-grade` (professor)

```ts
const user = getUserOr401(req);
const { class_slug, item_slug, user_id, points_earned, max_points_override } = parseBody(req);
const { class_id } = resolveClassOr404(class_slug);
requireMembership(class_id, user.id, 'professor');

const sb = supabaseForUser(req);
const item = await getItemBySlug(sb, class_id, item_slug);

await sb.from('item_grades').upsert({
  item_id: item.id, user_id, points_earned, max_points_override, graded_at: new Date().toISOString(), grader_id: user.id
});
return json({ ok: true });
```

*(Apply the same skeleton: auth → resolve → authorize → validate → act.)*

---

# 6) Performance & Scaling

* **Indexes** (added) for all hot paths.
* **Materialized views** (optional) for `v_module_totals` and `v_final_grades`; refresh:

  * On item grade change
  * On adjustments change
  * On items/constituents/modules updates
    (Use triggers or a scheduled `pg_cron` job.)
* **Pagination** on large listings (submissions).
* **Response shaping**: return only what the FE needs (avoid giant joins for dashboards).
* **Caching**: Edge Function response caching is risky with per-user auth; keep TTL tiny or skip.

---

# 7) Monitoring, Logging, Alerting

* Log **auth failures (401/403)**, **rate-limit hits (429)**, and **Storage signing** events.
* Add a simple **health** endpoint.
* Consider **error reporting** (Sentry) on Edge Functions.

---

# 8) Migration & Testing Plan

1. Create schema (Section 1).
2. Seed `classes`, `class_professors`, `class_students` test data.
3. Enable RLS (1.8) **after** initial seeding.
4. Set up Storage bucket.
5. Implement Edge Function helpers; wire `/me`, enrollment.
6. Implement student read APIs (`/my/...`) using RLS views.
7. Implement submission flows (upload/url/text/json).
8. Implement professor actions (grades, adjustments, submissions listing).
9. CI sync endpoints with GitHub OIDC.
10. Add rate limits and CSP.

**Local dev tips**

* Use **Supabase CLI** for local Postgres/Auth/Storage.
* Create **test users** via Auth API; insert into `class_professors`/`class_students`.
* Use **service role** only in secure server contexts (never in FE).

---

# 9) Appendix — JSON Schemas (selected)

**ItemSyncItem**

```json
{
  "type":"object",
  "required":["slug","title","constituent_slug","max_points","parts"],
  "properties":{
    "slug":{"type":"string"},
    "title":{"type":"string"},
    "constituent_slug":{"type":"string"},
    "max_points":{"type":"number"},
    "due_at":{"type":["string","null"],"format":"date-time"},
    "deliver_policy":{"type":"object"},
    "penalty":{"type":"object"},
    "default_value":{"type":["number","null"]},
    "default_policy":{"type":"object"},
    "parts":{
      "type":"array",
      "items":{
        "type":"object",
        "required":["key","kind"],
        "properties":{
          "key":{"type":"string"},
          "kind":{"type":"string","enum":["file","text","url","json"]},
          "required":{"type":"boolean","default":true},
          "validation":{"type":"object"},
          "opens_at":{"type":["string","null"],"format":"date-time"},
          "closes_at":{"type":["string","null"],"format":"date-time"}
        }
      }
    },
    "source":{"type":"object"}
  }
}
```

**GradeUpsert**

```json
{
  "type":"object",
  "required":["class_slug","item_slug","user_id","points_earned"],
  "properties":{
    "class_slug":{"type":"string"},
    "item_slug":{"type":"string"},
    "user_id":{"type":"string","format":"uuid"},
    "points_earned":{"type":"number"},
    "max_points_override":{"type":["number","null"]}
  }
}
```

---

## Final notes

* This doc **expands** prior contracts with: `/me`, concrete request/response examples, rate limits, idempotency, pagination, and pseudo-code skeletons for Edge Functions.
* The **security posture** stays tight: RLS-first, **no** client-side authority, short-lived signed URLs, and CI strictly via **GitHub OIDC**.
* The model is intentionally **generic** (Items vs “homeworks”), so you can later add exams, projects, CSV imports, or richer policy functions without rewiring fundamentals.
