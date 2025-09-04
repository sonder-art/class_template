-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.class_members (
  class_id uuid NOT NULL,
  user_id uuid NOT NULL,
  role text NOT NULL CHECK (role = ANY (ARRAY['professor'::text, 'student'::text])),
  enrolled_at timestamp with time zone DEFAULT now(),
  enrollment_token_id bigint,
  enrollment_status text DEFAULT 'active'::text CHECK (enrollment_status = ANY (ARRAY['active'::text, 'inactive'::text, 'pending'::text])),
  CONSTRAINT class_members_pkey PRIMARY KEY (class_id, user_id),
  CONSTRAINT class_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT class_members_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.classes (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  slug text NOT NULL UNIQUE,
  title text NOT NULL,
  description text,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  repo_name text NOT NULL,
  professor_github_username text,
  CONSTRAINT classes_pkey PRIMARY KEY (id)
);
CREATE TABLE public.constituents (
  id text NOT NULL,
  slug text NOT NULL UNIQUE,
  name text NOT NULL,
  description text,
  module_id text NOT NULL,
  weight numeric NOT NULL CHECK (weight >= 0::numeric AND weight <= 100::numeric),
  type text NOT NULL,
  max_attempts integer DEFAULT 3,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  class_id uuid,
  is_current boolean DEFAULT true,
  CONSTRAINT constituents_pkey PRIMARY KEY (id),
  CONSTRAINT constituents_module_id_fkey FOREIGN KEY (module_id) REFERENCES public.modules(id),
  CONSTRAINT constituents_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.enrollment_tokens (
  id bigint NOT NULL DEFAULT nextval('enrollment_tokens_id_seq'::regclass),
  class_id uuid,
  token_hash text NOT NULL,
  expires_at timestamp with time zone NOT NULL,
  max_uses integer DEFAULT 0,
  uses integer DEFAULT 0,
  created_by uuid,
  created_at timestamp with time zone DEFAULT now(),
  is_active boolean DEFAULT true,
  CONSTRAINT enrollment_tokens_pkey PRIMARY KEY (id),
  CONSTRAINT enrollment_tokens_created_by_fkey FOREIGN KEY (created_by) REFERENCES auth.users(id),
  CONSTRAINT enrollment_tokens_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.grading_adjustments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL,
  item_id text NOT NULL,
  class_id uuid NOT NULL,
  professor_id uuid NOT NULL,
  adjustment_type text NOT NULL CHECK (adjustment_type = ANY (ARRAY['manual_grade'::text, 'bonus'::text, 'penalty'::text, 'extension'::text])),
  points numeric NOT NULL,
  reason text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT grading_adjustments_pkey PRIMARY KEY (id),
  CONSTRAINT grading_adjustments_professor_id_fkey FOREIGN KEY (professor_id) REFERENCES auth.users(id),
  CONSTRAINT grading_adjustments_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id),
  CONSTRAINT grading_adjustments_student_id_fkey FOREIGN KEY (student_id) REFERENCES auth.users(id)
);
CREATE TABLE public.grading_policies (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  module_id text,
  class_id uuid NOT NULL,
  policy_name text NOT NULL,
  version text NOT NULL DEFAULT '1.0'::text,
  policy_rules jsonb NOT NULL CHECK (policy_rules ? 'grading_rules'::text AND jsonb_typeof(policy_rules -> 'grading_rules'::text) = 'array'::text),
  description text,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT grading_policies_pkey PRIMARY KEY (id),
  CONSTRAINT grading_policies_module_id_fkey FOREIGN KEY (module_id) REFERENCES public.modules(id),
  CONSTRAINT grading_policies_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.items (
  id text NOT NULL,
  constituent_slug text NOT NULL,
  title text NOT NULL,
  file_path text,
  points numeric NOT NULL CHECK (points > 0::numeric),
  due_date timestamp with time zone,
  delivery_type text NOT NULL CHECK (delivery_type = ANY (ARRAY['text'::text, 'url'::text, 'file'::text, 'upload'::text, 'code'::text])),
  instructions text,
  grading_criteria jsonb,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  class_id uuid,
  is_current boolean DEFAULT true,
  CONSTRAINT items_pkey PRIMARY KEY (id),
  CONSTRAINT items_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id),
  CONSTRAINT items_constituent_slug_fkey FOREIGN KEY (constituent_slug) REFERENCES public.constituents(slug)
);
CREATE TABLE public.modules (
  id text NOT NULL,
  name text NOT NULL,
  description text,
  weight numeric NOT NULL CHECK (weight >= 0::numeric AND weight <= 100::numeric),
  order_index integer NOT NULL,
  color text,
  icon text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  class_id uuid,
  is_current boolean DEFAULT true,
  CONSTRAINT modules_pkey PRIMARY KEY (id),
  CONSTRAINT modules_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.profiles (
  user_id uuid NOT NULL,
  github_username text UNIQUE,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT profiles_pkey PRIMARY KEY (user_id),
  CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.student_submissions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL,
  item_id text NOT NULL,
  class_id uuid NOT NULL,
  attempt_number integer NOT NULL DEFAULT 1 CHECK (attempt_number > 0),
  submission_data jsonb NOT NULL,
  submitted_at timestamp with time zone DEFAULT now(),
  graded_at timestamp with time zone,
  raw_score numeric CHECK (raw_score >= 0::numeric),
  adjusted_score numeric CHECK (adjusted_score >= 0::numeric),
  feedback text,
  grader_id uuid,
  graded_attempt_number integer,
  has_newer_version boolean DEFAULT false,
  CONSTRAINT student_submissions_pkey PRIMARY KEY (id),
  CONSTRAINT student_submissions_grader_id_fkey FOREIGN KEY (grader_id) REFERENCES auth.users(id),
  CONSTRAINT student_submissions_student_id_fkey FOREIGN KEY (student_id) REFERENCES auth.users(id),
  CONSTRAINT student_submissions_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id),
  CONSTRAINT student_submissions_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id)
);