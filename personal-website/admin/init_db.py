"""
Initialize Database - Uses existing Supabase connection
از اتصال موجود Supabase استفاده میکنه
"""

import os
import sys
import httpx

# Add parent directory to path to access the same .env
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env from bot directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

print("=" * 60)
print("🚀 راه‌اندازی دیتابیس CMS سایت شخصی")
print("=" * 60)
print(f"\n🔗 URL: {SUPABASE_URL}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ اطلاعات Supabase در .env موجود نیست")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ اتصال به Supabase برقرار شد")

# SQL to create tables via Supabase SQL API
SQL_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS blog_posts (
    id SERIAL PRIMARY KEY,
    title_fa TEXT,
    title_en TEXT,
    excerpt_fa TEXT,
    excerpt_en TEXT,
    content_fa TEXT,
    content_en TEXT,
    category_fa TEXT,
    category_en TEXT,
    date TIMESTAMP DEFAULT NOW(),
    published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal_info (
    id SERIAL PRIMARY KEY,
    name_fa TEXT,
    name_en TEXT,
    title_fa TEXT,
    title_en TEXT,
    about_fa TEXT,
    about_en TEXT,
    email TEXT,
    location TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    category TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

def try_create_via_sql_api():
    """Try creating tables via Supabase SQL API (service role required)"""
    print("\n📡 تلاش برای ایجاد جداول از طریق SQL API...")
    
    # Try the query endpoint
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Try different SQL endpoints
    endpoints = [
        f"{SUPABASE_URL}/rest/v1/rpc/query",
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        f"{SUPABASE_URL}/pg/query",
    ]
    
    for endpoint in endpoints:
        try:
            response = httpx.post(
                endpoint,
                json={"query": SQL_CREATE_TABLES},
                headers=headers,
                timeout=30
            )
            if response.status_code in [200, 201]:
                print(f"   ✅ موفق از طریق: {endpoint}")
                return True
        except Exception as e:
            pass
    
    return False

def check_and_create_tables():
    """Check if tables exist and try to create them"""
    print("\n📊 بررسی جداول...")
    
    tables_config = {
        'blog_posts': {
            'sample': {
                'title_fa': 'اولین پست بلاگ',
                'title_en': 'First Blog Post',
                'excerpt_fa': 'این یک پست نمونه است',
                'excerpt_en': 'This is a sample post',
                'content_fa': 'محتوای کامل پست نمونه به فارسی',
                'content_en': 'Full sample post content in English',
                'category_fa': 'عمومی',
                'category_en': 'General',
                'published': True
            }
        },
        'personal_info': {
            'sample': {
                'name_fa': 'امید شجاعی',
                'name_en': 'Omid Shojaei',
                'title_fa': 'توسعه‌دهنده و برنامه‌نویس',
                'title_en': 'Developer & Programmer',
                'about_fa': 'علاقه‌مند به ساخت نرم‌افزارهای کاربردی',
                'about_en': 'Passionate about building useful software',
                'email': 'your@email.com',
                'location': 'Iran'
            }
        },
        'skills': {
            'samples': [
                {'name': 'Python', 'progress': 90, 'category': 'Programming', 'order_index': 1},
                {'name': 'JavaScript', 'progress': 85, 'category': 'Programming', 'order_index': 2},
                {'name': 'HTML/CSS', 'progress': 95, 'category': 'Programming', 'order_index': 3},
                {'name': 'Git', 'progress': 85, 'category': 'Tools', 'order_index': 4},
                {'name': 'Telegram Bot API', 'progress': 90, 'category': 'Tools', 'order_index': 5},
            ]
        }
    }
    
    results = {}
    
    for table_name, config in tables_config.items():
        try:
            # Try to select from table
            result = supabase.table(table_name).select('id').limit(1).execute()
            
            # Table exists
            if result.data:
                print(f"   ✅ {table_name}: موجود ({len(result.data)} رکورد)")
                results[table_name] = 'exists_with_data'
            else:
                print(f"   ✅ {table_name}: موجود (خالی)")
                results[table_name] = 'exists_empty'
                
        except Exception as e:
            error_str = str(e)
            if 'PGRST205' in error_str or 'does not exist' in error_str.lower() or '42P01' in error_str:
                print(f"   ❌ {table_name}: موجود نیست")
                results[table_name] = 'not_exists'
            else:
                print(f"   ⚠️ {table_name}: خطای ناشناخته - {e}")
                results[table_name] = 'error'
    
    return results, tables_config

def insert_sample_data(tables_config):
    """Insert sample data into tables"""
    print("\n📝 افزودن داده‌های نمونه...")
    
    # Personal info
    try:
        existing = supabase.table('personal_info').select('id').limit(1).execute()
        if not existing.data:
            supabase.table('personal_info').insert(tables_config['personal_info']['sample']).execute()
            print("   ✅ اطلاعات شخصی اضافه شد")
        else:
            print("   ℹ️ اطلاعات شخصی از قبل موجود")
    except Exception as e:
        print(f"   ⚠️ personal_info: {e}")
    
    # Skills
    try:
        existing = supabase.table('skills').select('id').limit(1).execute()
        if not existing.data:
            for skill in tables_config['skills']['samples']:
                supabase.table('skills').insert(skill).execute()
            print("   ✅ مهارت‌ها اضافه شدند")
        else:
            print("   ℹ️ مهارت‌ها از قبل موجود")
    except Exception as e:
        print(f"   ⚠️ skills: {e}")
    
    # Blog post
    try:
        existing = supabase.table('blog_posts').select('id').limit(1).execute()
        if not existing.data:
            supabase.table('blog_posts').insert(tables_config['blog_posts']['sample']).execute()
            print("   ✅ پست نمونه اضافه شد")
        else:
            print("   ℹ️ پست‌ها از قبل موجود")
    except Exception as e:
        print(f"   ⚠️ blog_posts: {e}")

def print_manual_instructions():
    """Print SQL for manual creation"""
    print("\n" + "=" * 60)
    print("📋 کد SQL برای ساخت دستی جداول:")
    print("=" * 60)
    print("""
در Supabase Dashboard → SQL Editor این کد رو اجرا کنید:

```sql
CREATE TABLE IF NOT EXISTS blog_posts (
    id SERIAL PRIMARY KEY,
    title_fa TEXT, title_en TEXT,
    excerpt_fa TEXT, excerpt_en TEXT,
    content_fa TEXT, content_en TEXT,
    category_fa TEXT, category_en TEXT,
    date TIMESTAMP DEFAULT NOW(),
    published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal_info (
    id SERIAL PRIMARY KEY,
    name_fa TEXT, name_en TEXT,
    title_fa TEXT, title_en TEXT,
    about_fa TEXT, about_en TEXT,
    email TEXT, location TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    category TEXT, order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```
""")

if __name__ == '__main__':
    # Try SQL API first
    try_create_via_sql_api()
    
    # Check tables
    results, config = check_and_create_tables()
    
    # Check if any table doesn't exist
    missing = [t for t, status in results.items() if status == 'not_exists']
    
    if missing:
        print(f"\n⚠️ جداول زیر موجود نیستند: {', '.join(missing)}")
        print_manual_instructions()
    else:
        # All tables exist, insert sample data
        insert_sample_data(config)
        print("\n" + "=" * 60)
        print("✅ همه چیز آماده است!")
        print("=" * 60)
        print("\n🌐 پنل مدیریت: http://localhost:5001/admin")

