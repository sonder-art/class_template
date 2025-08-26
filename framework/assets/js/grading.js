console.log('🚀 GRADING.JS LOADED - Starting grading interface');

class GradingInterface {
    constructor() {
        console.log('🏗️ GradingInterface constructor called');
        this.classId = null;
        this.supabase = null;
        this.modules = [];
        this.constituents = [];
        this.items = [];
        this.students = [];
        this.submissions = [];
        
        this.init();
    }
    
    async init() {
        console.log('🔧 Grading interface initializing...');
        
        // Try meta tags first
        this.classId = document.querySelector('meta[name="class-id"]')?.content;
        let url = document.querySelector('meta[name="supabase-url"]')?.content;
        let key = document.querySelector('meta[name="supabase-anon-key"]')?.content;
        
        // Fallback to FrameworkConfig
        if (!this.classId && window.FrameworkConfig) {
            console.log('📄 Using FrameworkConfig fallback');
            this.classId = window.FrameworkConfig.classContext?.classId;
            url = window.FrameworkConfig.supabase?.url;
            key = window.FrameworkConfig.supabase?.anonKey;
        }
        
        // Fallback to authConfig
        if (!url && window.authConfig) {
            console.log('🔑 Using authConfig fallback');
            url = window.authConfig.supabase_url;
            key = window.authConfig.supabase_anon_key;
        }
        
        console.log('🔧 Config found:', { 
            classId: this.classId, 
            hasUrl: !!url, 
            hasKey: !!key 
        });
        
        if (!this.classId || !url || !key) {
            console.error('❌ Missing configuration');
            document.getElementById('grading-interface').innerHTML = '<p>Configuration error. Missing class ID or Supabase config.</p>';
            return;
        }
        
        this.supabase = supabase.createClient(url, key);
        
        await this.loadData();
        this.render();
    }
    
    async loadData() {
        console.log('🔄 Loading grading data...');
        console.log('🔍 DEBUG: Using class_id for queries:', this.classId);
        
        // Execute queries with detailed logging
        console.log('📊 Executing database queries...');
        
        const modulesQuery = this.supabase.from('modules').select('*').eq('class_id', this.classId).eq('is_current', true);
        const constituentsQuery = this.supabase.from('constituents').select('*').eq('class_id', this.classId).eq('is_current', true);
        const itemsQuery = this.supabase.from('items').select('*').eq('class_id', this.classId).eq('is_current', true);
        const submissionsQuery = this.supabase.from('student_submissions').select('*').eq('class_id', this.classId).order('submitted_at', { ascending: false });
        
        console.log('🔍 Items query details:', {
            table: 'items',
            filters: ['class_id =', this.classId, 'is_current = true']
        });
        
        // Execute main queries (excluding members for now)
        const [modules, constituents, items, submissions] = await Promise.all([
            modulesQuery,
            constituentsQuery,
            itemsQuery,
            submissionsQuery
        ]);
        
        // Two-step query for class members and profiles
        console.log('👥 Fetching class members and profiles...');
        const membersQuery = this.supabase
            .from('class_members')
            .select('*')
            .eq('class_id', this.classId);
            
        const members = await membersQuery;
        let enhancedMembers = { data: [], error: null };
        
        if (members.data && members.data.length > 0) {
            console.log(`📋 Found ${members.data.length} class members, fetching profiles...`);
            const userIds = members.data.map(m => m.user_id);
            
            const profilesQuery = this.supabase
                .from('profiles')
                .select('user_id, full_name, github_username, avatar_url')
                .in('user_id', userIds);
            
            const profiles = await profilesQuery;
            
            if (profiles.data) {
                console.log(`👤 Found ${profiles.data.length} profiles, merging data...`);
                // Merge profile data into member records
                enhancedMembers.data = members.data.map(member => ({
                    ...member,
                    profiles: profiles.data.find(p => p.user_id === member.user_id) || null
                }));
            } else {
                console.log('⚠️ No profiles found, using members without profile data');
                // Use members without profile data
                enhancedMembers.data = members.data.map(member => ({
                    ...member,
                    profiles: null
                }));
            }
        } else if (members.error) {
            console.error('❌ Members query failed:', members.error);
            enhancedMembers.error = members.error;
        } else {
            console.log('📋 No class members found');
        }
        
        // Log query results in detail
        console.log('📊 Raw query results:');
        console.log('  - Modules query result:', modules);
        console.log('  - Constituents query result:', constituents);
        console.log('  - Items query result:', items);
        console.log('  - Enhanced members result:', enhancedMembers);
        console.log('  - Submissions query result:', submissions);
        
        this.modules = modules.data || [];
        this.constituents = constituents.data || [];
        this.items = items.data || [];
        
        // Handle member data with error checking
        if (enhancedMembers.error) {
            console.error('❌ Class members query failed:', enhancedMembers.error);
            console.log('🔄 Attempting to continue without member data...');
            this.students = [];
            this.professors = [];
        } else {
            const allMembers = enhancedMembers.data || [];
            this.students = allMembers.filter(m => m.role === 'student');
            this.professors = allMembers.filter(m => m.role === 'professor');
            console.log(`✅ Successfully processed ${allMembers.length} members (${this.students.length} students, ${this.professors.length} professors)`);
        }
        
        this.submissions = submissions.data || [];
        
        console.log('📊 Grading data loaded:', {
            modules: this.modules.length,
            constituents: this.constituents.length, 
            items: this.items.length,
            students: this.students.length,
            submissions: this.submissions.length
        });
        
        console.log('🔍 DEBUG: Class ID being used:', this.classId);
        
        console.log('🧱 Modules details:', this.modules.map(m => ({
            id: m.id,
            name: m.name,
            class_id: m.class_id,
            is_current: m.is_current
        })));
        
        console.log('🔧 Constituents details:', this.constituents.map(c => ({
            id: c.id,
            slug: c.slug,
            name: c.name,
            module_id: c.module_id,
            class_id: c.class_id,
            is_current: c.is_current
        })));
        
        console.log('📋 Items details:', this.items.map(i => ({
            id: i.id,
            title: i.title,
            constituent_slug: i.constituent_slug,
            points: i.points,
            class_id: i.class_id,
            is_current: i.is_current,
            is_active: i.is_active
        })));
        
        console.log('📝 Submissions details:', this.submissions.map(s => ({
            id: s.id,
            student_id: s.student_id,
            item_id: s.item_id,
            attempt: s.attempt_number,
            submitted_at: s.submitted_at,
            class_id: s.class_id
        })));
        
        console.log('👥 Students only:', this.students.map(s => ({
            user_id: s.user_id,
            role: s.role,
            name: s.profiles?.full_name || 'Unknown',
            github_username: s.profiles?.github_username || 'Unknown'
        })));
        
        console.log('👨‍🏫 Professors only:', this.professors.map(p => ({
            user_id: p.user_id,
            role: p.role,
            name: p.profiles?.full_name || 'Unknown',
            github_username: p.profiles?.github_username || 'Unknown'
        })));
        
        // Separate professor and student submissions
        const professorIds = this.professors.map(p => p.user_id);
        const studentIds = this.students.map(s => s.user_id);
        
        // Fallback: if we don't have member data, try to identify current user's submissions
        if (professorIds.length === 0 && window.authState?.user?.id) {
            console.log('🔄 No professor data found, using current user as professor fallback');
            professorIds.push(window.authState.user.id);
        }
        
        this.professorSubmissions = this.submissions.filter(s => professorIds.includes(s.student_id));
        this.studentSubmissions = this.submissions.filter(s => studentIds.includes(s.student_id));
        
        console.log('📨 Student submissions:', this.studentSubmissions.length);
        console.log('🧪 Professor test submissions:', this.professorSubmissions.length);
        
        // Find the specific item we're looking for
        const githubOAuthItem = this.items.find(item => item.id === 'github_oauth_setup' || item.title?.includes('GitHub OAuth'));
        console.log('🎯 GitHub OAuth Item found:', githubOAuthItem);
        
        // Find submissions for that specific item
        if (githubOAuthItem) {
            const itemSubmissions = this.submissions.filter(s => s.item_id === githubOAuthItem.id);
            const professorTestSubmissions = this.professorSubmissions.filter(s => s.item_id === githubOAuthItem.id);
            console.log('📨 All submissions for GitHub OAuth item:', itemSubmissions);
            console.log('🧪 Professor test submissions for GitHub OAuth item:', professorTestSubmissions);
        }
    }
    
    render() {
        const container = document.getElementById('grading-interface');
        container.innerHTML = `
            <div style="margin: 20px 0;">
                <button onclick="window.location.reload()" style="margin-bottom: 10px; padding: 8px 16px; background: var(--theme-accent-primary); color: white; border: none; border-radius: 4px; cursor: pointer;">🔄 Refresh Data</button>
                
                <select id="module-select">
                    <option value="">Select Module...</option>
                    ${this.modules.map(m => `<option value="${m.id}">${m.name}</option>`).join('')}
                </select>
                
                <select id="constituent-select" disabled>
                    <option value="">Select Constituent...</option>
                </select>
                
                <select id="item-select" disabled>
                    <option value="">Select Item...</option>
                </select>
            </div>
            
            <div id="grade-table" style="display: none;"></div>
            
            ${this.renderProfessorTestSubmissionsSection()}
        `;
        
        document.getElementById('module-select').onchange = (e) => this.selectModule(e.target.value);
        document.getElementById('constituent-select').onchange = (e) => this.selectConstituent(e.target.value);
        document.getElementById('item-select').onchange = (e) => this.selectItem(e.target.value);
    }
    
    selectModule(moduleId) {
        const filtered = this.constituents.filter(c => c.module_id === moduleId);
        
        const select = document.getElementById('constituent-select');
        select.innerHTML = '<option value="">Select Constituent...</option>' + 
            filtered.map(c => `<option value="${c.slug}">${c.name}</option>`).join('');
        select.disabled = false;
        
        document.getElementById('item-select').disabled = true;
        document.getElementById('grade-table').style.display = 'none';
    }
    
    selectConstituent(slug) {
        const filtered = this.items.filter(i => i.constituent_slug === slug);
        
        const select = document.getElementById('item-select');
        select.innerHTML = '<option value="">Select Item...</option>' + 
            filtered.map(i => `<option value="${i.id}">${i.title} (${i.points} pts)</option>`).join('');
        select.disabled = false;
        
        document.getElementById('grade-table').style.display = 'none';
    }
    
    selectItem(itemId) {
        const item = this.items.find(i => i.id === itemId);
        if (!item) return;
        
        const tableHtml = `
            <h3>${item.title} - ${item.points} points</h3>
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th>Student</th>
                    <th>Grade</th>
                    <th>Comments</th>
                </tr>
                ${this.students.map(s => this.renderStudentRow(s, item)).join('')}
            </table>
        `;
        
        document.getElementById('grade-table').innerHTML = tableHtml;
        document.getElementById('grade-table').style.display = 'block';
        
        document.querySelectorAll('.grade-input, .comment-input').forEach(input => {
            input.onchange = () => this.saveGrade(input);
        });
    }
    
    renderStudentRow(student, item) {
        const submission = this.submissions.find(s => 
            s.student_id === student.user_id && s.item_id === item.id
        );
        
        const name = student.profiles?.full_name || 'Unknown';
        const grade = submission?.raw_score || '';
        const comment = submission?.feedback || '';
        
        return `
            <tr>
                <td>${name}</td>
                <td>
                    <input type="number" 
                           class="grade-input"
                           value="${grade}"
                           min="0" max="${item.points}"
                           data-student="${student.user_id}"
                           data-item="${item.id}">
                </td>
                <td>
                    <input type="text" 
                           class="comment-input"
                           value="${comment}"
                           data-student="${student.user_id}"
                           data-item="${item.id}">
                </td>
            </tr>
        `;
    }
    
    renderProfessorTestSubmissionsSection() {
        if (!this.professorSubmissions || this.professorSubmissions.length === 0) {
            return '<div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 4px; color: #666;">🧪 No professor test submissions found.</div>';
        }
        
        // Group submissions by item
        const submissionsByItem = {};
        this.professorSubmissions.forEach(submission => {
            const item = this.items.find(i => i.id === submission.item_id);
            const itemTitle = item ? item.title : submission.item_id;
            
            if (!submissionsByItem[submission.item_id]) {
                submissionsByItem[submission.item_id] = {
                    item: item,
                    title: itemTitle,
                    submissions: []
                };
            }
            submissionsByItem[submission.item_id].submissions.push(submission);
        });
        
        return `
            <div style="margin-top: 30px; border-top: 2px solid #e9ecef; padding-top: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #495057;">🧪 Professor Test Submissions</h3>
                    <button id="toggle-professor-submissions" onclick="const content = document.getElementById('professor-submissions-content'); content.style.display = content.style.display === 'none' ? 'block' : 'none'; this.textContent = this.textContent === '👁️ Show' ? '🙈 Hide' : '👁️ Show';" 
                            style="margin-left: 10px; padding: 4px 8px; font-size: 12px; background: #6c757d; color: white; border: none; border-radius: 3px; cursor: pointer;">👁️ Show</button>
                </div>
                <div id="professor-submissions-content" style="display: none;">
                    <p style="font-style: italic; color: #6c757d; margin-bottom: 15px;">
                        These are test submissions from professors for testing and demonstration purposes. 
                        They are kept separate from actual student submissions.
                    </p>
                    ${Object.entries(submissionsByItem).map(([itemId, data]) => `
                        <div style="margin-bottom: 20px; border: 1px solid #dee2e6; border-radius: 4px; padding: 15px; background: #f8f9fa;">
                            <h4 style="margin: 0 0 10px 0; color: #495057;">${data.title} (${data.item?.points || 'N/A'} points)</h4>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #e9ecef;">
                                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Professor</th>
                                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Attempt</th>
                                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Submitted</th>
                                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Type</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.submissions.map(submission => {
                                        const professor = this.professors.find(p => p.user_id === submission.student_id);
                                        const professorName = professor?.profiles?.full_name || professor?.profiles?.github_username || 'Unknown Professor';
                                        const submissionType = JSON.parse(submission.submission_data || '{}').type || 'unknown';
                                        
                                        return `
                                            <tr>
                                                <td style="padding: 8px; border: 1px solid #dee2e6;">${professorName}</td>
                                                <td style="padding: 8px; border: 1px solid #dee2e6;">#${submission.attempt_number}</td>
                                                <td style="padding: 8px; border: 1px solid #dee2e6;">${new Date(submission.submitted_at).toLocaleString()}</td>
                                                <td style="padding: 8px; border: 1px solid #dee2e6;">${submissionType}</td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    async saveGrade(input) {
        const studentId = input.dataset.student;
        const itemId = input.dataset.item;
        const isGrade = input.classList.contains('grade-input');
        
        const submission = this.submissions.find(s => 
            s.student_id === studentId && s.item_id === itemId
        );
        
        const data = {
            [isGrade ? 'raw_score' : 'feedback']: input.value
        };
        
        if (submission) {
            await this.supabase
                .from('student_submissions')
                .update(data)
                .eq('id', submission.id);
        } else {
            const newSubmission = {
                student_id: studentId,
                item_id: itemId,
                class_id: this.classId,
                attempt_number: 1,
                submission_data: JSON.stringify({type: 'manual'}),
                submitted_at: new Date().toISOString(),
                ...data
            };
            
            const result = await this.supabase
                .from('student_submissions')
                .insert(newSubmission);
                
            if (result.data) {
                this.submissions.push(result.data[0]);
            }
        }
        
        input.style.backgroundColor = '#d4edda';
        setTimeout(() => input.style.backgroundColor = '', 1000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOMContentLoaded fired - checking for grading-interface');
    const gradingElement = document.getElementById('grading-interface');
    console.log('🔍 grading-interface element found:', !!gradingElement);
    
    if (gradingElement) {
        console.log('✅ Creating new GradingInterface instance');
        new GradingInterface();
    } else {
        console.log('❌ No grading-interface element found');
    }
});// Force cache bust 1755474897
