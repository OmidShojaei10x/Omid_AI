"""
Create Supabase Tables for Personal Website CMS
ایجاد جداول در Supabase برای پنل مدیریت سایت شخصی
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ خطا: SUPABASE_URL یا SUPABASE_API_KEY در فایل .env تنظیم نشده")
    print(f"   SUPABASE_URL: {'✅ تنظیم شده' if SUPABASE_URL else '❌ تنظیم نشده'}")
    print(f"   SUPABASE_API_KEY: {'✅ تنظیم شده' if SUPABASE_KEY else '❌ تنظیم نشده'}")
    exit(1)

print(f"🔗 اتصال به Supabase...")
print(f"   URL: {SUPABASE_URL[:50]}...")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL queries to create tables
CREATE_BLOG_POSTS = """
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
    date TIMESTAMP,
    published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
"""

CREATE_PERSONAL_INFO = """
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
"""

CREATE_SKILLS = """
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    category TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

def check_table_exists(table_name):
    """Check if a table exists by trying to query it"""
    try:
        result = supabase.table(table_name).select('id').limit(1).execute()
        return True
    except Exception as e:
        if 'does not exist' in str(e) or '42P01' in str(e):
            return False
        # Table exists but might be empty or have other issues
        return True

def create_tables():
    """Create all necessary tables"""
    print("\n📊 بررسی و ایجاد جداول...")
    
    tables_to_check = [
        ('blog_posts', 'پست‌های بلاگ'),
        ('personal_info', 'اطلاعات شخصی'),
        ('skills', 'مهارت‌ها')
    ]
    
    results = {}
    for table_name, persian_name in tables_to_check:
        exists = check_table_exists(table_name)
        results[table_name] = exists
        status = "✅ موجود" if exists else "❌ موجود نیست"
        print(f"   {persian_name} ({table_name}): {status}")
    
    # If tables don't exist, we need to create them via Supabase Dashboard
    missing_tables = [name for name, exists in results.items() if not exists]
    
    if missing_tables:
        print("\n⚠️  جداول زیر وجود ندارند و باید ساخته شوند:")
        for table in missing_tables:
            print(f"   - {table}")
        
        print("\n📝 لطفاً این SQL را در Supabase SQL Editor اجرا کنید:")
        print("-" * 50)
        print(CREATE_BLOG_POSTS)
        print(CREATE_PERSONAL_INFO)
        print(CREATE_SKILLS)
        print("-" * 50)
        
        return False
    else:
        print("\n✅ همه جداول موجود هستند!")
        return True

def insert_sample_data():
    """Insert sample data if tables are empty"""
    print("\n📝 بررسی و افزودن داده‌های نمونه...")
    
    # Check if blog_posts is empty
    try:
        posts = supabase.table('blog_posts').select('id').limit(1).execute()
        if not posts.data:
            print("   افزودن پست نمونه...")
            supabase.table('blog_posts').insert({
                'title_fa': 'اولین پست بلاگ',
                'title_en': 'First Blog Post',
                'excerpt_fa': 'این یک پست نمونه است',
                'excerpt_en': 'This is a sample post',
                'content_fa': 'محتوای پست نمونه به فارسی',
                'content_en': 'Sample post content in English',
                'category_fa': 'عمومی',
                'category_en': 'General',
                'published': True
            }).execute()
            print("   ✅ پست نمونه اضافه شد")
        else:
            print("   ✅ پست‌ها موجود هستند")
    except Exception as e:
        print(f"   ⚠️ خطا در افزودن پست: {e}")
    
    # Check if personal_info is empty
    try:
        info = supabase.table('personal_info').select('id').limit(1).execute()
        if not info.data:
            print("   افزودن اطلاعات شخصی نمونه...")
            supabase.table('personal_info').insert({
                'name_fa': 'امید شجاعی',
                'name_en': 'Omid Shojaei',
                'title_fa': 'توسعه‌دهنده و برنامه‌نویس',
                'title_en': 'Developer & Programmer',
                'about_fa': 'علاقه‌مند به ساخت نرم‌افزارهای کاربردی',
                'about_en': 'Passionate about building useful software',
                'email': 'your@email.com',
                'location': 'Iran'
            }).execute()
            print("   ✅ اطلاعات شخصی اضافه شد")
        else:
            print("   ✅ اطلاعات شخصی موجود است")
    except Exception as e:
        print(f"   ⚠️ خطا در افزودن اطلاعات: {e}")
    
    # Check if skills is empty
    try:
        skills = supabase.table('skills').select('id').limit(1).execute()
        if not skills.data:
            print("   افزودن مهارت‌های نمونه...")
            sample_skills = [
                {'name': 'Python', 'progress': 90, 'category': 'Programming', 'order_index': 1},
                {'name': 'JavaScript', 'progress': 85, 'category': 'Programming', 'order_index': 2},
                {'name': 'HTML/CSS', 'progress': 95, 'category': 'Programming', 'order_index': 3},
                {'name': 'Git', 'progress': 85, 'category': 'Tools', 'order_index': 4},
                {'name': 'Telegram Bot API', 'progress': 90, 'category': 'Tools', 'order_index': 5},
            ]
            for skill in sample_skills:
                supabase.table('skills').insert(skill).execute()
            print("   ✅ مهارت‌ها اضافه شدند")
        else:
            print("   ✅ مهارت‌ها موجود هستند")
    except Exception as e:
        print(f"   ⚠️ خطا در افزودن مهارت‌ها: {e}")

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 راه‌اندازی دیتابیس سایت شخصی")
    print("=" * 50)
    
    if create_tables():
        insert_sample_data()
    
    print("\n" + "=" * 50)
    print("✅ عملیات تکمیل شد!")
    print("=" * 50)

