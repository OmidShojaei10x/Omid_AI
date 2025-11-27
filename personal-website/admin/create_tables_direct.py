"""
Create tables using direct PostgreSQL connection
ایجاد جداول با اتصال مستقیم به PostgreSQL
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD") or os.getenv("DB_PASSWORD")

# Extract project reference from URL
if SUPABASE_URL:
    PROJECT_REF = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
else:
    PROJECT_REF = None

print("=" * 60)
print("🚀 ایجاد جداول با اتصال مستقیم به PostgreSQL")
print("=" * 60)

# SQL to create tables
CREATE_TABLES_SQL = """
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

INSERT_SAMPLE_DATA_SQL = """
-- داده‌های نمونه - اطلاعات شخصی
INSERT INTO personal_info (name_fa, name_en, title_fa, title_en, about_fa, about_en, email, location)
SELECT 'امید شجاعی', 'Omid Shojaei', 'توسعه‌دهنده و برنامه‌نویس', 'Developer & Programmer',
       'علاقه‌مند به ساخت نرم‌افزارهای کاربردی و اتوماسیون', 'Passionate about building useful software',
       'your@email.com', 'Iran'
WHERE NOT EXISTS (SELECT 1 FROM personal_info LIMIT 1);

-- مهارت‌ها
INSERT INTO skills (name, progress, category, order_index)
SELECT * FROM (VALUES 
    ('Python', 90, 'Programming', 1),
    ('JavaScript', 85, 'Programming', 2),
    ('HTML/CSS', 95, 'Programming', 3),
    ('Git', 85, 'Tools', 4),
    ('Telegram Bot API', 90, 'Tools', 5)
) AS v(name, progress, category, order_index)
WHERE NOT EXISTS (SELECT 1 FROM skills LIMIT 1);

-- پست نمونه
INSERT INTO blog_posts (title_fa, title_en, excerpt_fa, excerpt_en, content_fa, content_en, category_fa, category_en, published)
SELECT 'اولین پست بلاگ', 'First Blog Post',
       'این یک پست نمونه برای تست سیستم است', 'This is a sample post for testing',
       'محتوای کامل پست به فارسی...', 'Full content in English...',
       'عمومی', 'General', true
WHERE NOT EXISTS (SELECT 1 FROM blog_posts LIMIT 1);
"""

def get_db_url():
    """Construct database URL"""
    if not PROJECT_REF:
        return None
    
    # Try different password sources
    password = DB_PASSWORD
    
    if not password:
        # Try to extract from SUPABASE_KEY (service role key contains the password sometimes)
        # This is a long shot but worth trying
        password = os.getenv("POSTGRES_PASSWORD")
    
    if not password:
        return None
    
    # Supabase PostgreSQL connection string
    return f"postgresql://postgres.{PROJECT_REF}:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

def create_tables_psycopg2():
    """Create tables using psycopg2"""
    import psycopg2
    
    db_url = get_db_url()
    
    if not db_url:
        print("\n❌ رمز دیتابیس (SUPABASE_DB_PASSWORD) در .env تنظیم نشده")
        print("\nبرای پیدا کردن رمز دیتابیس:")
        print("1. برید به Supabase Dashboard")
        print("2. Settings → Database")
        print("3. Connection string → URI رو کپی کنید")
        print("4. رمز عبور رو از URI استخراج کنید")
        print("\nسپس در .env اضافه کنید:")
        print("SUPABASE_DB_PASSWORD=your-password-here")
        return False
    
    print(f"\n🔗 اتصال به دیتابیس...")
    print(f"   پروژه: {PROJECT_REF}")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ اتصال برقرار شد!")
        
        # Create tables
        print("\n📊 ایجاد جداول...")
        cursor.execute(CREATE_TABLES_SQL)
        print("✅ جداول ساخته شدند!")
        
        # Insert sample data
        print("\n📝 افزودن داده‌های نمونه...")
        cursor.execute(INSERT_SAMPLE_DATA_SQL)
        print("✅ داده‌ها اضافه شدند!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ خطا در اتصال: {e}")
        print("\nممکن است رمز عبور اشتباه باشد یا IP شما مجاز نباشد.")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        return False

def verify_tables():
    """Verify tables were created"""
    from supabase import create_client
    
    print("\n🔍 بررسی جداول...")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    tables = ['blog_posts', 'personal_info', 'skills']
    all_ok = True
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            count = len(result.data) if result.data else 0
            print(f"   ✅ {table}: {count} رکورد")
        except Exception as e:
            print(f"   ❌ {table}: خطا - {e}")
            all_ok = False
    
    return all_ok

if __name__ == '__main__':
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ خطا: متغیرهای Supabase تنظیم نشده‌اند")
        sys.exit(1)
    
    # Try direct PostgreSQL connection
    if create_tables_psycopg2():
        verify_tables()
        print("\n" + "=" * 60)
        print("✅ همه چیز آماده است!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ لطفاً جداول را به صورت دستی در Supabase بسازید")
        print("=" * 60)

