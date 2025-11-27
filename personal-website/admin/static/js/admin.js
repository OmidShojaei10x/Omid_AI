// Admin Panel JavaScript

const API_BASE = '';

// Check authentication on load
window.addEventListener('DOMContentLoaded', async () => {
    const isAuth = await checkAuth();
    if (!isAuth) {
        window.location.href = '/admin/login';
        return;
    }
    
    initNavigation();
    loadPosts();
    loadPersonalInfo();
    loadSkills();
    initModals();
});

// ==========================================
// Authentication
// ==========================================

async function checkAuth() {
    try {
        const response = await fetch('/admin/check-auth');
        return response.ok;
    } catch (error) {
        return false;
    }
}

document.getElementById('logoutBtn')?.addEventListener('click', async () => {
    await fetch('/admin/logout', { method: 'POST' });
    window.location.href = '/admin/login';
});

// ==========================================
// Navigation
// ==========================================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));
            
            item.classList.add('active');
            document.getElementById(`${section}-section`).classList.add('active');
        });
    });
}

// ==========================================
// Blog Posts
// ==========================================

async function loadPosts() {
    try {
        const response = await fetch('/api/posts');
        const result = await response.json();
        
        if (result.success) {
            displayPosts(result.data);
        }
    } catch (error) {
        console.error('Error loading posts:', error);
    }
}

function displayPosts(posts) {
    const container = document.getElementById('postsList');
    
    if (!posts || posts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5);">هنوز پستی وجود ندارد</p>';
        return;
    }
    
    container.innerHTML = posts.map(post => `
        <div class="post-card">
            <div class="post-header">
                <div>
                    <div class="post-title">${post.title_fa || post.title_en}</div>
                    <div class="post-meta">
                        ${post.category_fa || post.category_en || ''} • 
                        ${new Date(post.date).toLocaleDateString('fa-IR')} • 
                        ${post.published ? '✅ منتشر شده' : '⏳ پیش‌نویس'}
                    </div>
                </div>
                <div class="post-actions">
                    <button class="btn-edit" onclick="editPost(${post.id})">ویرایش</button>
                    <button class="btn-delete" onclick="deletePost(${post.id})">حذف</button>
                </div>
            </div>
        </div>
    `).join('');
}

document.getElementById('addPostBtn')?.addEventListener('click', () => {
    openPostModal();
});

function openPostModal(post = null) {
    const modal = document.getElementById('postModal');
    const form = document.getElementById('postForm');
    const title = document.getElementById('modalTitle');
    
    if (post) {
        title.textContent = 'ویرایش پست';
        document.getElementById('postId').value = post.id;
        document.getElementById('post_title_fa').value = post.title_fa || '';
        document.getElementById('post_title_en').value = post.title_en || '';
        document.getElementById('post_excerpt_fa').value = post.excerpt_fa || '';
        document.getElementById('post_excerpt_en').value = post.excerpt_en || '';
        document.getElementById('post_content_fa').value = post.content_fa || '';
        document.getElementById('post_content_en').value = post.content_en || '';
        document.getElementById('post_category_fa').value = post.category_fa || '';
        document.getElementById('post_category_en').value = post.category_en || '';
        document.getElementById('post_date').value = post.date ? post.date.split('T')[0] : '';
        document.getElementById('post_published').checked = post.published || false;
    } else {
        title.textContent = 'پست جدید';
        form.reset();
        document.getElementById('post_date').value = new Date().toISOString().split('T')[0];
    }
    
    modal.classList.add('active');
}

async function editPost(id) {
    try {
        const response = await fetch(`/api/posts/${id}`);
        const result = await response.json();
        
        if (result.success) {
            openPostModal(result.data);
        }
    } catch (error) {
        console.error('Error loading post:', error);
        alert('خطا در بارگذاری پست');
    }
}

async function deletePost(id) {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این پست را حذف کنید؟')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/posts/${id}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            loadPosts();
        } else {
            alert('خطا در حذف پست');
        }
    } catch (error) {
        console.error('Error deleting post:', error);
        alert('خطا در حذف پست');
    }
}

document.getElementById('postForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        title_fa: document.getElementById('post_title_fa').value,
        title_en: document.getElementById('post_title_en').value,
        excerpt_fa: document.getElementById('post_excerpt_fa').value,
        excerpt_en: document.getElementById('post_excerpt_en').value,
        content_fa: document.getElementById('post_content_fa').value,
        content_en: document.getElementById('post_content_en').value,
        category_fa: document.getElementById('post_category_fa').value,
        category_en: document.getElementById('post_category_en').value,
        date: document.getElementById('post_date').value,
        published: document.getElementById('post_published').checked
    };
    
    const postId = document.getElementById('postId').value;
    
    try {
        const url = postId ? `/api/posts/${postId}` : '/api/posts';
        const method = postId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            closePostModal();
            loadPosts();
        } else {
            alert('خطا در ذخیره پست');
        }
    } catch (error) {
        console.error('Error saving post:', error);
        alert('خطا در ذخیره پست');
    }
});

function closePostModal() {
    document.getElementById('postModal').classList.remove('active');
}

document.querySelector('.close')?.addEventListener('click', closePostModal);
document.getElementById('cancelBtn')?.addEventListener('click', closePostModal);

// ==========================================
// Personal Info
// ==========================================

async function loadPersonalInfo() {
    try {
        const response = await fetch('/api/personal-info');
        const result = await response.json();
        
        if (result.success && result.data) {
            const data = result.data;
            document.getElementById('name_fa').value = data.name_fa || '';
            document.getElementById('name_en').value = data.name_en || '';
            document.getElementById('title_fa').value = data.title_fa || '';
            document.getElementById('title_en').value = data.title_en || '';
            document.getElementById('about_fa').value = data.about_fa || '';
            document.getElementById('about_en').value = data.about_en || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('location').value = data.location || '';
        }
    } catch (error) {
        console.error('Error loading personal info:', error);
    }
}

document.getElementById('personalForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name_fa: document.getElementById('name_fa').value,
        name_en: document.getElementById('name_en').value,
        title_fa: document.getElementById('title_fa').value,
        title_en: document.getElementById('title_en').value,
        about_fa: document.getElementById('about_fa').value,
        about_en: document.getElementById('about_en').value,
        email: document.getElementById('email').value,
        location: document.getElementById('location').value
    };
    
    try {
        const response = await fetch('/api/personal-info', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ اطلاعات با موفقیت ذخیره شد');
        } else {
            alert('❌ خطا در ذخیره اطلاعات');
        }
    } catch (error) {
        console.error('Error saving personal info:', error);
        alert('❌ خطا در ذخیره اطلاعات');
    }
});

// ==========================================
// Skills
// ==========================================

async function loadSkills() {
    try {
        const response = await fetch('/api/skills');
        const result = await response.json();
        
        if (result.success) {
            displaySkills(result.data);
        }
    } catch (error) {
        console.error('Error loading skills:', error);
    }
}

function displaySkills(skills) {
    const container = document.getElementById('skillsList');
    
    if (!skills || skills.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5);">هنوز مهارتی وجود ندارد</p>';
        return;
    }
    
    container.innerHTML = skills.map(skill => `
        <div class="skill-card">
            <div class="skill-info">
                <div class="skill-name">${skill.name}</div>
                <div class="skill-progress">سطح: ${skill.progress || 0}%</div>
            </div>
            <div class="post-actions">
                <button class="btn-edit" onclick="editSkill(${skill.id})">ویرایش</button>
                <button class="btn-delete" onclick="deleteSkill(${skill.id})">حذف</button>
            </div>
        </div>
    `).join('');
}

function initModals() {
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('postModal');
        if (e.target === modal) {
            closePostModal();
        }
    });
}

// Make functions global
window.editPost = editPost;
window.deletePost = deletePost;
window.editSkill = (id) => alert('قابلیت ویرایش مهارت به زودی اضافه می‌شود');
window.deleteSkill = async (id) => {
    if (!confirm('آیا مطمئن هستید؟')) return;
    try {
        const response = await fetch(`/api/skills/${id}`, { method: 'DELETE' });
        const result = await response.json();
        if (result.success) loadSkills();
    } catch (error) {
        alert('خطا در حذف مهارت');
    }
};

