"""
Setup Supabase Database - Create Tables
ایجاد جداول در Supabase با استفاده از اتصال مستقیم به دیتابیس
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Extract project reference from URL
if SUPABASE_URL:
    # https://xxxxx.supabase.co -> xxxxx
    PROJECT_REF = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
else:
    PROJECT_REF = None

print("=" * 60)
print("🚀 راه‌اندازی دیتابیس سایت شخصی")
print("=" * 60)

# Try using httpx to call SQL endpoint
import httpx

SQL_QUERIES = """
-- جدول پست‌های بلاگ
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

-- جدول اطلاعات شخصی
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

-- جدول مهارت‌ها
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    category TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

SAMPLE_DATA = [
    """INSERT INTO personal_info (name_fa, name_en, title_fa, title_en, about_fa, about_en, email, location)
    SELECT 'امید شجاعی', 'Omid Shojaei', 'توسعه‌دهنده و برنامه‌نویس', 'Developer & Programmer', 
    'علاقه‌مند به ساخت نرم‌افزارهای کاربردی و اتوماسیون', 'Passionate about building useful software and automation',
    'your@email.com', 'Iran'
    WHERE NOT EXISTS (SELECT 1 FROM personal_info LIMIT 1);""",
    
    """INSERT INTO skills (name, progress, category, order_index)
    SELECT 'Python', 90, 'Programming', 1
    WHERE NOT EXISTS (SELECT 1 FROM skills WHERE name = 'Python');""",
    
    """INSERT INTO skills (name, progress, category, order_index)
    SELECT 'JavaScript', 85, 'Programming', 2
    WHERE NOT EXISTS (SELECT 1 FROM skills WHERE name = 'JavaScript');""",
    
    """INSERT INTO skills (name, progress, category, order_index)
    SELECT 'HTML/CSS', 95, 'Programming', 3
    WHERE NOT EXISTS (SELECT 1 FROM skills WHERE name = 'HTML/CSS');""",
    
    """INSERT INTO skills (name, progress, category, order_index)
    SELECT 'Git', 85, 'Tools', 4
    WHERE NOT EXISTS (SELECT 1 FROM skills WHERE name = 'Git');""",
    
    """INSERT INTO skills (name, progress, category, order_index)
    SELECT 'Telegram Bot API', 90, 'Tools', 5
    WHERE NOT EXISTS (SELECT 1 FROM skills WHERE name = 'Telegram Bot API');""",
    
    """INSERT INTO blog_posts (title_fa, title_en, excerpt_fa, excerpt_en, content_fa, content_en, category_fa, category_en, published)
    SELECT 'اولین پست بلاگ', 'First Blog Post', 
    'این یک پست نمونه برای تست سیستم بلاگ است', 'This is a sample post to test the blog system',
    'محتوای کامل پست به فارسی...', 'Full post content in English...',
    'عمومی', 'General', true
    WHERE NOT EXISTS (SELECT 1 FROM blog_posts LIMIT 1);"""
]

def execute_sql_via_rest():
    """Try to execute SQL via Supabase REST API"""
    print("\n📡 تلاش برای اتصال به Supabase REST API...")
    
    # Try the sql endpoint (available in some Supabase versions)
    sql_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # This usually won't work without a custom function, but let's try
    try:
        response = httpx.post(sql_url, json={"query": SQL_QUERIES}, headers=headers, timeout=30)
        if response.status_code == 200:
            print("✅ جداول با موفقیت ساخته شدند!")
            return True
        else:
            print(f"   ⚠️ REST API: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ REST API خطا: {type(e).__name__}")
    
    return False

def try_direct_insert():
    """Try to create tables by attempting operations and let Supabase create them"""
    print("\n📝 تلاش برای ایجاد جداول با Supabase Client...")
    
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    tables_status = {
        'blog_posts': False,
        'personal_info': False,
        'skills': False
    }
    
    # Test each table
    for table in tables_status.keys():
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            tables_status[table] = True
            print(f"   ✅ جدول {table} موجود است")
        except Exception as e:
            error_str = str(e)
            if 'PGRST205' in error_str or 'does not exist' in error_str.lower():
                print(f"   ❌ جدول {table} موجود نیست")
            else:
                tables_status[table] = True
                print(f"   ✅ جدول {table} موجود است (خالی)")
    
    return all(tables_status.values())

def insert_sample_data():
    """Insert sample data into tables"""
    print("\n📝 افزودن داده‌های نمونه...")
    
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Insert personal info
    try:
        existing = supabase.table('personal_info').select('id').limit(1).execute()
        if not existing.data:
            supabase.table('personal_info').insert({
                'name_fa': 'امید شجاعی',
                'name_en': 'Omid Shojaei',
                'title_fa': 'توسعه‌دهنده و برنامه‌نویس',
                'title_en': 'Developer & Programmer',
                'about_fa': 'علاقه‌مند به ساخت نرم‌افزارهای کاربردی و اتوماسیون',
                'about_en': 'Passionate about building useful software and automation',
                'email': 'your@email.com',
                'location': 'Iran'
            }).execute()
            print("   ✅ اطلاعات شخصی اضافه شد")
        else:
            print("   ℹ️ اطلاعات شخصی از قبل موجود است")
    except Exception as e:
        print(f"   ⚠️ خطا در personal_info: {e}")
    
    # Insert skills
    try:
        existing = supabase.table('skills').select('id').limit(1).execute()
        if not existing.data:
            skills = [
                {'name': 'Python', 'progress': 90, 'category': 'Programming', 'order_index': 1},
                {'name': 'JavaScript', 'progress': 85, 'category': 'Programming', 'order_index': 2},
                {'name': 'HTML/CSS', 'progress': 95, 'category': 'Programming', 'order_index': 3},
                {'name': 'Git', 'progress': 85, 'category': 'Tools', 'order_index': 4},
                {'name': 'Telegram Bot API', 'progress': 90, 'category': 'Tools', 'order_index': 5},
            ]
            for skill in skills:
                supabase.table('skills').insert(skill).execute()
            print("   ✅ مهارت‌ها اضافه شدند")
        else:
            print("   ℹ️ مهارت‌ها از قبل موجود هستند")
    except Exception as e:
        print(f"   ⚠️ خطا در skills: {e}")
    
    # Insert sample blog post
    try:
        existing = supabase.table('blog_posts').select('id').limit(1).execute()
        if not existing.data:
            supabase.table('blog_posts').insert({
                'title_fa': 'اولین پست بلاگ',
                'title_en': 'First Blog Post',
                'excerpt_fa': 'این یک پست نمونه برای تست سیستم بلاگ است',
                'excerpt_en': 'This is a sample post to test the blog system',
                'content_fa': 'محتوای کامل پست به فارسی. این یک پست نمونه است که می‌توانید ویرایش یا حذف کنید.',
                'content_en': 'Full post content in English. This is a sample post that you can edit or delete.',
                'category_fa': 'عمومی',
                'category_en': 'General',
                'published': True
            }).execute()
            print("   ✅ پست نمونه اضافه شد")
        else:
            print("   ℹ️ پست‌ها از قبل موجود هستند")
    except Exception as e:
        print(f"   ⚠️ خطا در blog_posts: {e}")

def print_sql_instructions():
    """Print SQL instructions for manual creation"""
    print("\n" + "=" * 60)
    print("📋 دستورالعمل ساخت دستی جداول")
    print("=" * 60)
    print("""
برای ساخت جداول، لطفاً:

1. برید به: https://supabase.com/dashboard
2. پروژه خود را انتخاب کنید
3. از منوی سمت چپ، SQL Editor رو باز کنید
4. کد SQL زیر رو کپی و Paste کنید
5. روی Run کلیک کنید

""")
    print("-" * 60)
    print("""
-- جدول پست‌های بلاگ
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

-- جدول اطلاعات شخصی
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

-- جدول مهارت‌ها
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    category TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- داده‌های نمونه
INSERT INTO personal_info (name_fa, name_en, title_fa, title_en, email, location)
VALUES ('امید شجاعی', 'Omid Shojaei', 'توسعه‌دهنده', 'Developer', 'your@email.com', 'Iran');

INSERT INTO skills (name, progress, category, order_index) VALUES
('Python', 90, 'Programming', 1),
('JavaScript', 85, 'Programming', 2),
('HTML/CSS', 95, 'Programming', 3),
('Git', 85, 'Tools', 4),
('Telegram Bot API', 90, 'Tools', 5);

INSERT INTO blog_posts (title_fa, title_en, excerpt_fa, excerpt_en, category_fa, category_en, published)
VALUES ('اولین پست', 'First Post', 'پست نمونه', 'Sample post', 'عمومی', 'General', true);
""")
    print("-" * 60)

if __name__ == '__main__':
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ خطا: متغیرهای محیطی Supabase تنظیم نشده‌اند")
        sys.exit(1)
    
    print(f"\n🔗 پروژه: {PROJECT_REF}")
    
    # Try REST API
    if execute_sql_via_rest():
        insert_sample_data()
        print("\n✅ همه چیز آماده است!")
        sys.exit(0)
    
    # Check if tables exist
    if try_direct_insert():
        insert_sample_data()
        print("\n✅ همه چیز آماده است!")
        sys.exit(0)
    
    # If all else fails, print manual instructions
    print_sql_instructions()
    print("\n⚠️ جداول باید به صورت دستی ساخته شوند.")

