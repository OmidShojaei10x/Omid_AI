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
    initAutoTranslation();
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
// Auto Translation (Persian to English)
// ==========================================

let translationTimeout = null;

async function translateText(text) {
    if (!text || text.trim() === '') return '';
    
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        const result = await response.json();
        
        if (result.success) {
            return result.translation;
        }
        return '';
    } catch (error) {
        console.error('Translation error:', error);
        return '';
    }
}

function initAutoTranslation() {
    // Map of Persian fields to their English counterparts
    const translationPairs = [
        // Post fields
        { fa: 'post_title_fa', en: 'post_title_en' },
        { fa: 'post_excerpt_fa', en: 'post_excerpt_en' },
        { fa: 'post_content_fa', en: 'post_content_en' },
        { fa: 'post_category_fa', en: 'post_category_en' },
        // Personal info fields
        { fa: 'name_fa', en: 'name_en' },
        { fa: 'title_fa', en: 'title_en' },
        { fa: 'about_fa', en: 'about_en' },
    ];
    
    translationPairs.forEach(pair => {
        const faInput = document.getElementById(pair.fa);
        const enInput = document.getElementById(pair.en);
        
        if (faInput && enInput) {
            // Add translation button
            addTranslateButton(faInput, enInput);
            
            // Auto-translate on blur (when user leaves the field)
            faInput.addEventListener('blur', async () => {
                const text = faInput.value.trim();
                if (text && !enInput.value.trim()) {
                    enInput.placeholder = '🔄 در حال ترجمه...';
                    const translation = await translateText(text);
                    if (translation) {
                        enInput.value = translation;
                        enInput.placeholder = '';
                        showNotification('✅ ترجمه انجام شد');
                    } else {
                        enInput.placeholder = '';
                    }
                }
            });
        }
    });
}

function addTranslateButton(faInput, enInput) {
    // Create a translate button next to the English input
    const wrapper = enInput.parentElement;
    if (!wrapper) return;
    
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn-translate';
    btn.innerHTML = '🔄 ترجمه خودکار';
    btn.style.cssText = `
        margin-top: 0.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-size: 0.85rem;
        cursor: pointer;
        font-family: inherit;
        transition: all 0.3s;
    `;
    
    btn.addEventListener('mouseenter', () => {
        btn.style.transform = 'translateY(-2px)';
        btn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
    });
    
    btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translateY(0)';
        btn.style.boxShadow = 'none';
    });
    
    btn.addEventListener('click', async () => {
        const text = faInput.value.trim();
        if (!text) {
            showNotification('⚠️ ابتدا متن فارسی را وارد کنید');
            return;
        }
        
        btn.innerHTML = '⏳ در حال ترجمه...';
        btn.disabled = true;
        
        const translation = await translateText(text);
        
        if (translation) {
            enInput.value = translation;
            showNotification('✅ ترجمه انجام شد');
        } else {
            showNotification('❌ خطا در ترجمه');
        }
        
        btn.innerHTML = '🔄 ترجمه خودکار';
        btn.disabled = false;
    });
    
    wrapper.appendChild(btn);
}

function showNotification(message) {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        padding: 1rem 2rem;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        border-radius: 12px;
        font-size: 1rem;
        z-index: 9999;
        animation: slideUp 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { opacity: 0; transform: translateX(-50%) translateY(20px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
    @keyframes slideDown {
        from { opacity: 1; transform: translateX(-50%) translateY(0); }
        to { opacity: 0; transform: translateX(-50%) translateY(20px); }
    }
`;
document.head.appendChild(style);

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
        document.getElementById('postId').value = '';
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
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '⏳ در حال ذخیره...';
    submitBtn.disabled = true;
    
    // Auto-translate empty English fields before saving
    const pairs = [
        { fa: 'post_title_fa', en: 'post_title_en' },
        { fa: 'post_excerpt_fa', en: 'post_excerpt_en' },
        { fa: 'post_content_fa', en: 'post_content_en' },
        { fa: 'post_category_fa', en: 'post_category_en' },
    ];
    
    for (const pair of pairs) {
        const faValue = document.getElementById(pair.fa).value.trim();
        const enInput = document.getElementById(pair.en);
        if (faValue && !enInput.value.trim()) {
            const translation = await translateText(faValue);
            if (translation) {
                enInput.value = translation;
            }
        }
    }
    
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
            showNotification('✅ پست ذخیره شد');
        } else {
            alert('خطا در ذخیره پست');
        }
    } catch (error) {
        console.error('Error saving post:', error);
        alert('خطا در ذخیره پست');
    }
    
    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
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
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '⏳ در حال ذخیره...';
    submitBtn.disabled = true;
    
    // Auto-translate empty English fields
    const pairs = [
        { fa: 'name_fa', en: 'name_en' },
        { fa: 'title_fa', en: 'title_en' },
        { fa: 'about_fa', en: 'about_en' },
    ];
    
    for (const pair of pairs) {
        const faValue = document.getElementById(pair.fa).value.trim();
        const enInput = document.getElementById(pair.en);
        if (faValue && !enInput.value.trim()) {
            const translation = await translateText(faValue);
            if (translation) {
                enInput.value = translation;
            }
        }
    }
    
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
            showNotification('✅ اطلاعات ذخیره شد');
        } else {
            alert('❌ خطا در ذخیره اطلاعات');
        }
    } catch (error) {
        console.error('Error saving personal info:', error);
        alert('❌ خطا در ذخیره اطلاعات');
    }
    
    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
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
