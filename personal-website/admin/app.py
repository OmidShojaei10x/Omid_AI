"""
CMS Admin Panel - Flask Backend
پنل مدیریت محتوا برای سایت شخصی
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
import hashlib
import httpx
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-this-secret-key-in-production')
CORS(app)

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL و SUPABASE_API_KEY باید در .env تنظیم شوند")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Admin credentials (در production از دیتابیس استفاده کنید)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', 
    hashlib.sha256('admin123'.encode()).hexdigest())  # Default: admin123

# ==========================================
# Authentication
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True, 'message': 'ورود موفق'})
        else:
            return jsonify({'success': False, 'message': 'نام کاربری یا رمز عبور اشتباه'}), 401
    
    return render_template('login.html')

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'خروج موفق'})

@app.route('/admin/check-auth')
def check_auth():
    if 'logged_in' in session and session['logged_in']:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401

# ==========================================
# Admin Panel Pages
# ==========================================

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('dashboard.html')

# ==========================================
# API Endpoints - Blog Posts
# ==========================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all blog posts"""
    try:
        response = supabase.table('blog_posts').select('*').order('created_at', desc=True).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    """Create new blog post"""
    try:
        data = request.get_json()
        
        post_data = {
            'title_fa': data.get('title_fa', ''),
            'title_en': data.get('title_en', ''),
            'excerpt_fa': data.get('excerpt_fa', ''),
            'excerpt_en': data.get('excerpt_en', ''),
            'content_fa': data.get('content_fa', ''),
            'content_en': data.get('content_en', ''),
            'category_fa': data.get('category_fa', ''),
            'category_en': data.get('category_en', ''),
            'date': data.get('date', datetime.now().isoformat()),
            'published': data.get('published', False),
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('blog_posts').insert(post_data).execute()
        return jsonify({'success': True, 'data': response.data[0]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get single blog post"""
    try:
        response = supabase.table('blog_posts').select('*').eq('id', post_id).execute()
        if response.data:
            return jsonify({'success': True, 'data': response.data[0]})
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    """Update blog post"""
    try:
        data = request.get_json()
        
        update_data = {}
        if 'title_fa' in data:
            update_data['title_fa'] = data['title_fa']
        if 'title_en' in data:
            update_data['title_en'] = data['title_en']
        if 'excerpt_fa' in data:
            update_data['excerpt_fa'] = data['excerpt_fa']
        if 'excerpt_en' in data:
            update_data['excerpt_en'] = data['excerpt_en']
        if 'content_fa' in data:
            update_data['content_fa'] = data['content_fa']
        if 'content_en' in data:
            update_data['content_en'] = data['content_en']
        if 'category_fa' in data:
            update_data['category_fa'] = data['category_fa']
        if 'category_en' in data:
            update_data['category_en'] = data['category_en']
        if 'published' in data:
            update_data['published'] = data['published']
        if 'date' in data:
            update_data['date'] = data['date']
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        response = supabase.table('blog_posts').update(update_data).eq('id', post_id).execute()
        return jsonify({'success': True, 'data': response.data[0] if response.data else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """Delete blog post"""
    try:
        supabase.table('blog_posts').delete().eq('id', post_id).execute()
        return jsonify({'success': True, 'message': 'Post deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API Endpoints - Personal Info
# ==========================================

@app.route('/api/personal-info', methods=['GET'])
def get_personal_info():
    """Get personal information"""
    try:
        response = supabase.table('personal_info').select('*').limit(1).execute()
        if response.data:
            return jsonify({'success': True, 'data': response.data[0]})
        return jsonify({'success': True, 'data': {}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personal-info', methods=['PUT'])
@login_required
def update_personal_info():
    """Update personal information"""
    try:
        data = request.get_json()
        
        # Check if record exists
        existing = supabase.table('personal_info').select('*').limit(1).execute()
        
        if existing.data:
            # Update
            response = supabase.table('personal_info').update(data).eq('id', existing.data[0]['id']).execute()
        else:
            # Create
            response = supabase.table('personal_info').insert(data).execute()
        
        return jsonify({'success': True, 'data': response.data[0] if response.data else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API Endpoints - Skills
# ==========================================

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get all skills"""
    try:
        response = supabase.table('skills').select('*').order('order_index').execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/skills', methods=['POST'])
@login_required
def create_skill():
    """Create new skill"""
    try:
        data = request.get_json()
        response = supabase.table('skills').insert(data).execute()
        return jsonify({'success': True, 'data': response.data[0]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/skills/<int:skill_id>', methods=['PUT'])
@login_required
def update_skill(skill_id):
    """Update skill"""
    try:
        data = request.get_json()
        response = supabase.table('skills').update(data).eq('id', skill_id).execute()
        return jsonify({'success': True, 'data': response.data[0] if response.data else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/skills/<int:skill_id>', methods=['DELETE'])
@login_required
def delete_skill(skill_id):
    """Delete skill"""
    try:
        supabase.table('skills').delete().eq('id', skill_id).execute()
        return jsonify({'success': True, 'message': 'Skill deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# API Endpoints - Translation (Auto Persian to English)
# ==========================================

@app.route('/api/translate', methods=['POST'])
@login_required
def translate_text():
    """Translate Persian text to English using OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return jsonify({'success': False, 'error': 'OpenAI API key not configured'}), 500
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': True, 'translation': ''})
        
        # Call OpenAI API
        response = httpx.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a translator. Translate the following Persian text to English. Only return the translation, nothing else. Keep the same tone and style.'
                    },
                    {
                        'role': 'user',
                        'content': text
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 2000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            translation = result['choices'][0]['message']['content'].strip()
            return jsonify({'success': True, 'translation': translation})
        else:
            return jsonify({'success': False, 'error': f'OpenAI API error: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# Run App
# ==========================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

