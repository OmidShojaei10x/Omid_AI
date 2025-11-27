# 🎛️ پنل مدیریت سایت شخصی

پنل مدیریت محتوا برای سایت شخصی با Flask و Supabase

## ✨ ویژگی‌ها

- 📝 مدیریت پست‌های بلاگ
- 👤 ویرایش اطلاعات شخصی
- 💪 مدیریت مهارت‌ها
- 🔐 سیستم احراز هویت
- 🌐 پشتیبانی فارسی و انگلیسی

## 🚀 نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
cd admin
pip install -r requirements.txt
```

### 2. تنظیمات .env

در فایل `.env` در ریشه پروژه، این متغیرها رو اضافه کنید:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
FLASK_SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=sha256-hash-of-password
```

برای تولید hash رمز عبور:
```python
import hashlib
hashlib.sha256('your-password'.encode()).hexdigest()
```

### 3. ایجاد جداول در Supabase

در Supabase SQL Editor این کوئری‌ها رو اجرا کنید:

```sql
-- جدول پست‌های بلاگ
CREATE TABLE blog_posts (
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

-- جدول اطلاعات شخصی
CREATE TABLE personal_info (
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
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    category TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. اجرای سرور

```bash
python app.py
```

پنل مدیریت در آدرس زیر در دسترس خواهد بود:
- **http://localhost:5000/admin**

## 📝 استفاده

1. برید به `/admin/login`
2. با نام کاربری و رمز عبور وارد بشید
3. از منوی سمت راست بخش مورد نظر رو انتخاب کنید
4. محتوا رو ویرایش و ذخیره کنید

## 🔒 امنیت

- در production حتماً `FLASK_SECRET_KEY` قوی تنظیم کنید
- رمز عبور admin رو تغییر بدید
- بهتره از دیتابیس برای ذخیره کاربران استفاده کنید

## 📚 API Endpoints

### پست‌های بلاگ
- `GET /api/posts` - دریافت همه پست‌ها
- `POST /api/posts` - ایجاد پست جدید
- `GET /api/posts/<id>` - دریافت یک پست
- `PUT /api/posts/<id>` - ویرایش پست
- `DELETE /api/posts/<id>` - حذف پست

### اطلاعات شخصی
- `GET /api/personal-info` - دریافت اطلاعات
- `PUT /api/personal-info` - ویرایش اطلاعات

### مهارت‌ها
- `GET /api/skills` - دریافت همه مهارت‌ها
- `POST /api/skills` - ایجاد مهارت جدید
- `PUT /api/skills/<id>` - ویرایش مهارت
- `DELETE /api/skills/<id>` - حذف مهارت

