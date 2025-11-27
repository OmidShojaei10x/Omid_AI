"""
Telegram Bot - Full Featured Version
بات تلگرام با امکانات کامل
"""

import asyncio
import logging
import os
import time
import httpx
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client, Client

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ─────────────────────────────────────────────────────────────────
#  تنظیمات اولیه
# ─────────────────────────────────────────────────────────────────

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN در .env تنظیم نشده است.")
if not SUPABASE_URL or not SUPABASE_API_KEY:
    raise RuntimeError("SUPABASE_URL یا SUPABASE_API_KEY در .env تنظیم نشده است.")
if not OPENAI_API_KEY:
    logger = logging.getLogger("telesummary-bot")
    logger.warning("OPENAI_API_KEY تنظیم نشده - قابلیت گزارش AI غیرفعال است.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telesummary-bot")

# ─────────────────────────────────────────────────────────────────
#  ثابت‌ها
# ─────────────────────────────────────────────────────────────────

# تعداد آیتم در هر صفحه
PAGE_SIZE = 5

BUTTON_HOME = "🏠 منوی اصلی"
BUTTON_REPORTS = "📊 گزارش‌ها"
BUTTON_GROUPS = "💬 گروه‌ها"
BUTTON_SETTINGS = "⚙️ تنظیمات"
BUTTON_HELP = "❓ راهنما"
BUTTON_PROFILE = "👤 پروفایل من"
BUTTON_CANCEL = "❌ انصراف"

MAIN_REPLY_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton(BUTTON_HOME), KeyboardButton(BUTTON_PROFILE)],
        [KeyboardButton(BUTTON_REPORTS), KeyboardButton(BUTTON_GROUPS)],
        [KeyboardButton(BUTTON_SETTINGS), KeyboardButton(BUTTON_HELP)],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)

ROLE_LEVELS = {
    "owner": 4,
    "admin": 3,
    "user": 1,
    "blocked": 0,
}

ROLE_LABELS = {
    "owner": "مالک",
    "admin": "ادمین",
    "user": "کاربر",
    "blocked": "مسدود",
}

# ─────────────────────────────────────────────────────────────────
#  سیستم چندزبانه - کامل
# ─────────────────────────────────────────────────────────────────

TRANSLATIONS = {
    "fa": {
        # عمومی
        "hello": "سلام {name}! 👋",
        "admin_menu": "🔐 منوی ادمین:",
        "back": "🔙 بازگشت",
        "cancel": "❌ انصراف",
        "home": "🏠 منوی اصلی",
        "yes": "✅ بله",
        "no": "❌ خیر",
        "error": "❌ خطایی رخ داد.",
        "use_menu": "از منو استفاده کنید یا /cancel برای لغو.",
        "need_username": "برای استفاده از بات باید username تلگرام داشته باشید.",
        
        # دکمه‌های منو
        "btn_home": "🏠 منوی اصلی",
        "btn_profile": "👤 پروفایل من",
        "btn_reports": "📊 گزارش‌ها",
        "btn_groups": "💬 گروه‌ها",
        "btn_settings": "⚙️ تنظیمات",
        "btn_help": "❓ راهنما",
        
        # منوی ادمین
        "user_management": "👥 مدیریت کاربران",
        "search_user": "🔍 جستجوی کاربر",
        "group_management": "💬 مدیریت گروه‌ها",
        "settings": "⚙️ تنظیمات",
        "stats": "📊 آمار",
        "audit_log": "📋 لاگ فعالیت‌ها",
        
        # مدیریت کاربران
        "select_role": "انتخاب نقش:",
        "add_user": "➕ افزودن کاربر با نقش {role}:",
        "send_user_info": "یکی از موارد زیر را ارسال کنید:\n• یوزرنیم (با یا بدون @)\n• فوروارد پیام از کاربر\n• آیدی عددی\n• ارسال Contact",
        "user_added": "✅ کاربر {username} با نقش {role} اضافه شد.",
        "user_exists": "⚠️ این کاربر قبلاً ثبت شده.",
        "user_exists_detail": "⚠️ این کاربر قبلاً ثبت شده.\n\n👤 کاربر: {username}\n🎭 نقش فعلی: {current_role}\n🎯 نقش جدید: {new_role}",
        "user_not_found": "کاربر یافت نشد.",
        "cannot_identify": "نتوانستم کاربر را شناسایی کنم.\nیوزرنیم، آیدی، فوروارد یا Contact ارسال کنید.",
        "invalid_id": "شناسه نامعتبر.",
        "invalid_role": "نقش نامعتبر.",
        "role_changed": "✅ نقش کاربر {username} به {role} تغییر کرد.",
        "user_deleted": "✅ کاربر {username} حذف شد.",
        "delete_error": "❌ خطا در حذف کاربر.",
        "confirm_delete": "⚠️ آیا از حذف کاربر @{username} مطمئن هستید؟\n\nاین عملیات قابل بازگشت نیست!",
        "yes_delete": "✅ بله، حذف کن",
        "no_cancel": "❌ خیر",
        "change_role": "🔄 تغییر نقش",
        "manage_groups": "💬 مدیریت گروه‌ها",
        "delete": "🗑 حذف",
        "select_new_role": "انتخاب نقش جدید:",
        "change_role_confirm": "آیا می‌خواهید سطح دسترسی این کاربر را تغییر دهید؟",
        "yes_change": "✅ بله، تغییر بده",
        "user_info": "👤 کاربر: {username}\n🔢 آیدی: {id}\n🎭 نقش: {role}\n📅 تاریخ ثبت: {date}\n✅ وضعیت: {status}",
        "user_groups_title": "💬 گروه‌های @{username}:\n✅ = دسترسی دارد | ❌ = دسترسی ندارد",
        "back_to_list": "🔙 بازگشت به لیست",
        "admin_back": "🏠 منوی ادمین",
        "search_prompt": "🔍 یوزرنیم کاربر مورد نظر را وارد کنید:",
        "search_results": "🔍 نتایج جستجو برای «{query}»:",
        "no_results": "نتیجه‌ای یافت نشد.",
        
        # دسترسی
        "operation_cancelled": "❌ عملیات لغو شد.",
        "no_access": "دسترسی شما معتبر نیست.",
        "no_admin": "دسترسی ادمین ندارید.",
        "active": "فعال",
        "inactive": "غیرفعال",
        
        # تنظیمات
        "settings_title": "⚙️ تنظیمات شما:\n\nبرای تغییر هر مورد روی آن کلیک کنید.",
        "language": "🌐 زبان",
        "notifications": "🔔 نوتیفیکیشن",
        "date_format": "📅 فرمت تاریخ",
        "page_size": "📄 تعداد در صفحه",
        "auto_report": "📊 گزارش خودکار",
        "select_language": "🌐 انتخاب زبان:",
        "lang_changed": "✅ زبان به {lang_name} تغییر کرد.",
        "notif_on": "روشن",
        "notif_off": "خاموش",
        "notif_status": "وضعیت فعلی: {status}",
        "notif_changed": "✅ نوتیفیکیشن {status} شد.",
        "date_shamsi": "شمسی",
        "date_miladi": "میلادی",
        "date_changed": "✅ فرمت تاریخ به {format} تغییر کرد.",
        "page_size_changed": "✅ تعداد در صفحه به {size} تغییر کرد.",
        "auto_report_on": "فعال",
        "auto_report_off": "غیرفعال",
        "auto_report_changed": "✅ گزارش خودکار {status} شد.",
        
        # گزارش‌ها
        "weekly_report": "📅 گزارش هفتگی",
        "monthly_report": "📆 گزارش ماهانه",
        "select_group": "گروه مورد نظر را انتخاب کنید:",
        "select_report_type": "نوع گزارش را انتخاب کنید:",
        "generating_report": "⏳ در حال تهیه گزارش...",
        "report_error": "❌ خطا در تهیه گزارش.",
        "no_groups": "شما به هیچ گروهی دسترسی ندارید.",
        "report_weekly": "هفتگی",
        "report_monthly": "ماهانه",
        "another_report": "📊 گزارش دیگر",
        
        # راهنما
        "help_text": "📚 راهنمای استفاده از بات:\n\n۱) «📊 گزارش‌ها» - دریافت گزارش گروه‌ها\n۲) «👤 پروفایل من» - مشاهده اطلاعات شما\n۳) «💬 گروه‌ها» - لیست گروه‌های شما\n۴) «⚙️ تنظیمات» - تنظیمات شخصی\n۵) /cancel - لغو عملیات جاری",
        
        # پروفایل
        "your_profile": "👤 پروفایل شما:\n\n📛 نام: {name}\n🆔 آیدی: {id}\n👤 یوزرنیم: @{username}\n🎭 نقش: {role}",
        "profile": "👤 پروفایل من",
        "reports": "📊 گزارش‌ها",
        "groups": "💬 گروه‌ها",
        "help": "❓ راهنما",
        
        # گروه‌ها
        "your_groups": "💬 گروه‌های شما:",
        "no_groups_access": "شما به هیچ گروهی دسترسی ندارید.",
        "send_group_number": "شماره گروه را ارسال کنید یا /cancel برای انصراف.",
        "invalid_number": "فقط شماره گروه را ارسال کنید.",
        "invalid_group_number": "شماره نامعتبر است.",
        
        # آمار
        "group_stats": "📊 آمار گروه «{title}»:\n\n📝 کل پیام‌ها: {total}\n📅 پیام‌های ۷ روز اخیر: {weekly}\n👥 کاربران فعال: {users}",
        
        # لاگ
        "recent_logs": "📋 آخرین فعالیت‌ها:",
        "no_logs": "لاگی ثبت نشده.",
    },
    "en": {
        # General
        "hello": "Hello {name}! 👋",
        "admin_menu": "🔐 Admin Menu:",
        "back": "🔙 Back",
        "cancel": "❌ Cancel",
        "home": "🏠 Main Menu",
        "yes": "✅ Yes",
        "no": "❌ No",
        "error": "❌ An error occurred.",
        "use_menu": "Use the menu or /cancel to abort.",
        "need_username": "You need a Telegram username to use this bot.",
        
        # Menu buttons
        "btn_home": "🏠 Main Menu",
        "btn_profile": "👤 My Profile",
        "btn_reports": "📊 Reports",
        "btn_groups": "💬 Groups",
        "btn_settings": "⚙️ Settings",
        "btn_help": "❓ Help",
        
        # Admin menu
        "user_management": "👥 User Management",
        "search_user": "🔍 Search User",
        "group_management": "💬 Group Management",
        "settings": "⚙️ Settings",
        "stats": "📊 Stats",
        "audit_log": "📋 Audit Log",
        
        # User management
        "select_role": "Select Role:",
        "add_user": "➕ Add user with role {role}:",
        "send_user_info": "Send one of the following:\n• Username (with or without @)\n• Forward a message from user\n• Numeric ID\n• Send Contact",
        "user_added": "✅ User {username} added with role {role}.",
        "user_exists": "⚠️ This user already exists.",
        "user_exists_detail": "⚠️ This user already exists.\n\n👤 User: {username}\n🎭 Current role: {current_role}\n🎯 New role: {new_role}",
        "user_not_found": "User not found.",
        "cannot_identify": "Could not identify the user.\nSend username, ID, forward or Contact.",
        "invalid_id": "Invalid ID.",
        "invalid_role": "Invalid role.",
        "role_changed": "✅ User {username} role changed to {role}.",
        "user_deleted": "✅ User {username} deleted.",
        "delete_error": "❌ Error deleting user.",
        "confirm_delete": "⚠️ Are you sure you want to delete @{username}?\n\nThis action cannot be undone!",
        "yes_delete": "✅ Yes, delete",
        "no_cancel": "❌ No",
        "change_role": "🔄 Change Role",
        "manage_groups": "💬 Manage Groups",
        "delete": "🗑 Delete",
        "select_new_role": "Select new role:",
        "change_role_confirm": "Do you want to change this user's access level?",
        "yes_change": "✅ Yes, change",
        "user_info": "👤 User: {username}\n🔢 ID: {id}\n🎭 Role: {role}\n📅 Registered: {date}\n✅ Status: {status}",
        "user_groups_title": "💬 Groups for @{username}:\n✅ = Has access | ❌ = No access",
        "back_to_list": "🔙 Back to list",
        "admin_back": "🏠 Admin Menu",
        "search_prompt": "🔍 Enter the username to search:",
        "search_results": "🔍 Search results for \"{query}\":",
        "no_results": "No results found.",
        
        # Access
        "operation_cancelled": "❌ Operation cancelled.",
        "no_access": "Your access is not valid.",
        "no_admin": "You don't have admin access.",
        "active": "Active",
        "inactive": "Inactive",
        
        # Settings
        "settings_title": "⚙️ Your Settings:\n\nClick on any option to change it.",
        "language": "🌐 Language",
        "notifications": "🔔 Notifications",
        "date_format": "📅 Date Format",
        "page_size": "📄 Page Size",
        "auto_report": "📊 Auto Report",
        "select_language": "🌐 Select Language:",
        "lang_changed": "✅ Language changed to {lang_name}.",
        "notif_on": "On",
        "notif_off": "Off",
        "notif_status": "Current status: {status}",
        "notif_changed": "✅ Notifications turned {status}.",
        "date_shamsi": "Shamsi",
        "date_miladi": "Gregorian",
        "date_changed": "✅ Date format changed to {format}.",
        "page_size_changed": "✅ Page size changed to {size}.",
        "auto_report_on": "enabled",
        "auto_report_off": "disabled",
        "auto_report_changed": "✅ Auto report {status}.",
        
        # Reports
        "weekly_report": "📅 Weekly Report",
        "monthly_report": "📆 Monthly Report",
        "select_group": "Select a group:",
        "select_report_type": "Select report type:",
        "generating_report": "⏳ Generating report...",
        "report_error": "❌ Error generating report.",
        "no_groups": "You don't have access to any groups.",
        "report_weekly": "Weekly",
        "report_monthly": "Monthly",
        "another_report": "📊 Another Report",
        
        # Help
        "help_text": "📚 How to use this bot:\n\n1) «📊 Reports» - Get group reports\n2) «👤 My Profile» - View your info\n3) «💬 Groups» - Your groups list\n4) «⚙️ Settings» - Personal settings\n5) /cancel - Cancel current operation",
        
        # Profile
        "your_profile": "👤 Your Profile:\n\n📛 Name: {name}\n🆔 ID: {id}\n👤 Username: @{username}\n🎭 Role: {role}",
        "profile": "👤 My Profile",
        "reports": "📊 Reports",
        "groups": "💬 Groups",
        "help": "❓ Help",
        
        # Groups
        "your_groups": "💬 Your Groups:",
        "no_groups_access": "You don't have access to any groups.",
        "send_group_number": "Send group number or /cancel to abort.",
        "invalid_number": "Please send only the group number.",
        "invalid_group_number": "Invalid number.",
        
        # Stats
        "group_stats": "📊 Stats for \"{title}\":\n\n📝 Total messages: {total}\n📅 Last 7 days: {weekly}\n👥 Active users: {users}",
        
        # Logs
        "recent_logs": "📋 Recent Activities:",
        "no_logs": "No logs recorded.",
    }
}

def t(key: str, lang: str = "fa", **kwargs) -> str:
    """دریافت متن ترجمه شده"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["fa"]).get(key, TRANSLATIONS["fa"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

async def get_user_lang(user_id: int) -> str:
    """دریافت زبان کاربر - همیشه فارسی"""
    return "fa"

ROLE_LABELS_FA = {
    "owner": "مالک",
    "admin": "ادمین",
    "user": "کاربر",
    "blocked": "مسدود",
}

ROLE_ICONS = {
    "owner": "👑",
    "admin": "🛡",
    "user": "👤",
    "blocked": "🚫",
}

ROLE_DEFAULT_PERMISSIONS = {
    "owner": {
        "manage_users", "manage_groups", "view_all_groups", "view_reports",
        "request_reports", "edit_permissions", "view_audit_logs",
        "export_data", "delete_data", "ai_priority_processing",
    },
    "admin": {
        "manage_users", "manage_groups", "view_all_groups", "view_reports",
        "request_reports", "edit_permissions", "view_audit_logs",
        "export_data", "ai_priority_processing",
    },
    "user": {"view_reports", "request_reports"},
    "blocked": set(),
}

# ─────────────────────────────────────────────────────────────────
#  تنظیمات پیش‌فرض کاربران
# ─────────────────────────────────────────────────────────────────

DEFAULT_USER_SETTINGS = {
    "language": "fa",           # fa | en
    "notifications": True,      # True | False
    "date_format": "shamsi",    # shamsi | miladi
    "page_size": 5,             # 5 | 10 | 15 | 20
    "auto_report": False,       # True | False
}

LANGUAGE_OPTIONS = {
    "fa": "🇮🇷 فارسی",
    "en": "🇬🇧 English",
}

DATE_FORMAT_OPTIONS = {
    "shamsi": "☀️ شمسی",
    "miladi": "📅 میلادی",
}

PAGE_SIZE_OPTIONS = [5, 10, 15, 20]

# ─────────────────────────────────────────────────────────────────
#  کش
# ─────────────────────────────────────────────────────────────────

class SimpleCache:
    def __init__(self, ttl: int = 60):
        self._cache: dict = {}
        self._ttl = ttl
    
    def get(self, key: str):
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value):
        self._cache[key] = (value, time.time())
    
    def invalidate(self, key: str):
        self._cache.pop(key, None)
    
    def clear(self):
        self._cache.clear()


user_cache = SimpleCache(ttl=120)
groups_cache = SimpleCache(ttl=300)

# ─────────────────────────────────────────────────────────────────
#  صف لاگ
# ─────────────────────────────────────────────────────────────────

log_queue: asyncio.Queue = None


async def init_log_queue():
    global log_queue
    log_queue = asyncio.Queue(maxsize=1000)


async def log_worker():
    """Background worker for processing log entries."""
    while True:
        row = None
        try:
            row = await log_queue.get()
            await asyncio.to_thread(_insert_log_row, row)
            log_queue.task_done()
        except Exception as e:
            logger.error("خطا در log_worker: %s", e)
            await asyncio.sleep(1)


def _insert_log_row(row: dict):
    try:
        supabase.table("telegram_updates").insert(row).execute()
    except Exception as e:
        logger.error("خطا در ذخیره لاگ: %s", e)


async def queue_log(update: Update):
    if log_queue is None:
        return
    try:
        row = _build_log_row(update)
        if row:
            try:
                log_queue.put_nowait(row)
            except asyncio.QueueFull:
                pass
    except Exception:
        pass


def _build_log_row(update: Update) -> Optional[dict]:
    """Build a log row from an Update object."""
    now = int(time.time())
    if update.message:
        msg = update.message
        chat = msg.chat
        from_user = msg.from_user
        return {
            "update_id": update.update_id,
            "update_type": "message",
            "chat_id": chat.id,
            "chat_type": chat.type,
            "chat_title": chat.title,
            "message_id": msg.message_id,
            "from_id": from_user.id if from_user else None,
            "from_is_bot": from_user.is_bot if from_user else None,
            "username": from_user.username if from_user else None,
            "first_name": from_user.first_name if from_user else None,
            "last_name": from_user.last_name if from_user else None,
            "language_code": from_user.language_code if from_user else None,
            "text": msg.text,
            "caption": msg.caption,
            "callback_data": None,
            "reply_to_message_id": msg.reply_to_message.message_id if msg.reply_to_message else None,
            "media_type": None,
            "file_id": None,
            "entities": msg.to_dict().get("entities"),
            "date_ts": int(msg.date.timestamp()) if msg.date else now,
            "date": datetime.utcnow().isoformat(),
            "raw": update.to_dict(),
        }
    if update.callback_query:
        cq = update.callback_query
        msg = cq.message
        chat = msg.chat if msg else None
        from_user = cq.from_user
        return {
            "update_id": update.update_id,
            "update_type": "callback_query",
            "chat_id": chat.id if chat else None,
            "chat_type": chat.type if chat else None,
            "chat_title": chat.title if chat else None,
            "message_id": msg.message_id if msg else None,
            "from_id": from_user.id if from_user else None,
            "from_is_bot": from_user.is_bot if from_user else None,
            "username": from_user.username if from_user else None,
            "first_name": from_user.first_name if from_user else None,
            "last_name": from_user.last_name if from_user else None,
            "language_code": from_user.language_code if from_user else None,
            "text": msg.text if msg else None,
            "caption": None,
            "callback_data": cq.data,
            "reply_to_message_id": msg.reply_to_message.message_id if msg and msg.reply_to_message else None,
            "media_type": None,
            "file_id": None,
            "entities": msg.to_dict().get("entities") if msg else None,
            "date_ts": now,
            "date": datetime.utcnow().isoformat(),
            "raw": update.to_dict(),
        }
    return None



# ─────────────────────────────────────────────────────────────────
#  Audit Log
# ─────────────────────────────────────────────────────────────────

def _db_insert_audit_log(action: str, actor_username: str, target_info: str, details: dict = None):
    """ثبت لاگ تغییرات"""
    try:
        supabase.table("audit_logs").insert({
            "action": action,
            "admin_username": actor_username,
            "target": target_info,
            "details": details or {},
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception as e:
        logger.error("خطا در ثبت audit log: %s", e)


async def log_audit(action: str, actor_username: str, target_info: str, details: dict = None):
    """ثبت async لاگ تغییرات"""
    await asyncio.to_thread(_db_insert_audit_log, action, actor_username, target_info, details)


# ─────────────────────────────────────────────────────────────────
#  توابع کمکی
# ─────────────────────────────────────────────────────────────────

@lru_cache(maxsize=256)
def normalize_username(username: Optional[str]) -> Optional[str]:
    if not username:
        return None
    return username.lstrip("@").strip().lower()


def get_user_effective_role(user: Optional[dict]) -> str:
    if not user:
        return "blocked"
    if not user.get("is_active", True):
        return "blocked"
    role = (user.get("role") or "").strip().lower()
    if role in ROLE_LEVELS:
        return role
    return "admin" if user.get("is_admin") else "user"


def get_user_permissions(user: Optional[dict]) -> set:
    if not user:
        return set()
    role = get_user_effective_role(user)
    perms = set(ROLE_DEFAULT_PERMISSIONS.get(role, set()))
    extra = user.get("extra_permissions")
    if isinstance(extra, list):
        perms.update(str(p) for p in extra)
    return perms


def can_see_all_groups(user: dict) -> bool:
    return "view_all_groups" in get_user_permissions(user) or user.get("allow_all_groups")


# ─────────────────────────────────────────────────────────────────
#  توابع دیتابیس
# ─────────────────────────────────────────────────────────────────

def _db_fetch_user_by_username(username: str) -> Optional[dict]:
    norm = normalize_username(username)
    if not norm:
        return None
    try:
        res = supabase.table("allowed_users").select("*").in_(
            "telegram_username", [norm, f"@{norm}", norm.lower(), f"@{norm.lower()}"]
        ).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.error("خطا در fetch user: %s", e)
        return None


def _db_fetch_user_by_id(user_id: int) -> Optional[dict]:
    try:
        res = supabase.table("allowed_users").select("*").eq(
            "telegram_user_id", user_id
        ).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.error("خطا در fetch user by id: %s", e)
        return None


async def fetch_allowed_user(username: Optional[str]) -> Optional[dict]:
    if not username:
        return None
    cache_key = f"user:{normalize_username(username)}"
    cached = user_cache.get(cache_key)
    if cached is not None:
        return cached
    user = await asyncio.to_thread(_db_fetch_user_by_username, username)
    if user:
        user_cache.set(cache_key, user)
    return user


async def fetch_allowed_user_by_id(user_id: int) -> Optional[dict]:
    cache_key = f"user_id:{user_id}"
    cached = user_cache.get(cache_key)
    if cached is not None:
        return cached
    user = await asyncio.to_thread(_db_fetch_user_by_id, user_id)
    if user:
        user_cache.set(cache_key, user)
    return user


def _db_get_all_groups() -> list:
    try:
        res = supabase.table("chat_groups").select("*").order("chat_title", desc=False).execute()
        return res.data or []
    except Exception as e:
        logger.error("خطا در دریافت گروه‌ها: %s", e)
        return []


def _db_get_user_groups(username: str) -> list:
    norm = normalize_username(username)
    if not norm:
        return []
    try:
        res = supabase.table("user_group_permissions").select("chat_title").in_(
            "telegram_username", [norm, f"@{norm}"]
        ).execute()
        titles = [r["chat_title"] for r in (res.data or []) if r.get("chat_title")]
        return sorted(set(titles))
    except Exception as e:
        logger.error("خطا در دریافت گروه‌های کاربر: %s", e)
        return []


async def get_accessible_groups_for_user(user: dict) -> list:
    if can_see_all_groups(user):
        cached = groups_cache.get("all_groups")
        if cached:
            return cached
        groups = await asyncio.to_thread(_db_get_all_groups)
        titles = list(dict.fromkeys(g.get("chat_title") for g in groups if g.get("chat_title")))
        groups_cache.set("all_groups", titles)
        return titles
    
    username = user.get("telegram_username")
    cache_key = f"groups:{normalize_username(username)}"
    cached = groups_cache.get(cache_key)
    if cached:
        return cached
    
    groups = await asyncio.to_thread(_db_get_user_groups, username)
    groups_cache.set(cache_key, groups)
    return groups


def _db_pending_set(user_id: int, mode: str):
    try:
        supabase.table("pending_requests").upsert(
            {"user_id": user_id, "mode": mode}, on_conflict="user_id"
        ).execute()
    except Exception as e:
        logger.error("خطا در set pending: %s", e)


def _db_pending_get(user_id: int) -> Optional[str]:
    try:
        res = supabase.table("pending_requests").select("mode").eq(
            "user_id", user_id
        ).limit(1).execute()
        return res.data[0]["mode"] if res.data else None
    except Exception as e:
        logger.error("خطا در get pending: %s", e)
        return None


def _db_pending_clear(user_id: int):
    try:
        supabase.table("pending_requests").delete().eq("user_id", user_id).execute()
    except Exception as e:
        logger.error("خطا در clear pending: %s", e)


async def set_pending_mode(user_id: int, mode: str):
    await asyncio.to_thread(_db_pending_set, user_id, mode)


async def get_pending_mode(user_id: int) -> Optional[str]:
    return await asyncio.to_thread(_db_pending_get, user_id)


async def clear_pending_mode(user_id: int):
    await asyncio.to_thread(_db_pending_clear, user_id)


def _db_get_all_users() -> list:
    try:
        res = supabase.table("allowed_users").select("*").order("created_at", desc=False).execute()
        return res.data or []
    except Exception as e:
        logger.error("خطا در دریافت کاربران: %s", e)
        return []


def _db_get_user_by_db_id(db_id: int) -> Optional[dict]:
    try:
        res = supabase.table("allowed_users").select("*").eq("id", db_id).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.error("خطا: %s", e)
        return None


def _db_insert_user(data: dict):
    supabase.table("allowed_users").insert(data).execute()


def _db_update_user(db_id: int, data: dict):
    supabase.table("allowed_users").update(data).eq("id", db_id).execute()


def _db_delete_user(db_id: int):
    supabase.table("allowed_users").delete().eq("id", db_id).execute()


def _db_search_users(query: str) -> list:
    """جستجوی کاربران"""
    try:
        res = supabase.table("allowed_users").select("*").ilike(
            "telegram_username", f"%{query}%"
        ).execute()
        return res.data or []
    except Exception as e:
        logger.error("خطا در جستجو: %s", e)
        return []


def _db_get_user_group_permissions(username: str) -> list:
    """گروه‌های یک کاربر"""
    norm = normalize_username(username)
    if not norm:
        return []
    try:
        res = supabase.table("user_group_permissions").select("*").in_(
            "telegram_username", [norm, f"@{norm}"]
        ).execute()
        return res.data or []
    except Exception as e:
        logger.error("خطا: %s", e)
        return []


def _db_add_user_group_permission(username: str, chat_title: str):
    """اضافه کردن گروه به کاربر"""
    norm = normalize_username(username)
    try:
        supabase.table("user_group_permissions").insert({
            "telegram_username": f"@{norm}",
            "chat_title": chat_title
        }).execute()
    except Exception as e:
        logger.error("خطا: %s", e)


def _db_remove_user_group_permission(username: str, chat_title: str):
    """حذف گروه از کاربر"""
    norm = normalize_username(username)
    try:
        supabase.table("user_group_permissions").delete().in_(
            "telegram_username", [norm, f"@{norm}"]
        ).eq("chat_title", chat_title).execute()
    except Exception as e:
        logger.error("خطا: %s", e)


def _db_get_audit_logs(limit: int = 20) -> list:
    """دریافت آخرین لاگ‌های تغییرات"""
    try:
        res = supabase.table("audit_logs").select("*").order(
            "created_at", desc=True
        ).limit(limit).execute()
        return res.data or []
    except Exception as e:
        logger.error("خطا در دریافت audit logs: %s", e)
        return []


def _db_get_user_settings(user_id: int) -> dict:
    """دریافت تنظیمات کاربر"""
    try:
        res = supabase.table("user_settings").select("*").eq(
            "telegram_user_id", user_id
        ).limit(1).execute()
        if res.data:
            return res.data[0]
        return {}
    except Exception as e:
        logger.error("خطا در دریافت تنظیمات: %s", e)
        return {}


def _db_save_user_settings(user_id: int, settings: dict):
    """ذخیره تنظیمات کاربر"""
    try:
        data = {"telegram_user_id": user_id, **settings}
        supabase.table("user_settings").upsert(
            data, on_conflict="telegram_user_id"
        ).execute()
    except Exception as e:
        logger.error("خطا در ذخیره تنظیمات: %s", e)


def _db_get_bot_settings() -> dict:
    """دریافت تنظیمات کلی بات"""
    try:
        res = supabase.table("bot_settings").select("*").limit(1).execute()
        if res.data:
            return res.data[0]
        return {}
    except Exception as e:
        logger.error("خطا در دریافت تنظیمات بات: %s", e)
        return {}


def _db_save_bot_settings(settings: dict):
    """ذخیره تنظیمات کلی بات"""
    try:
        data = {"id": 1, **settings}
        supabase.table("bot_settings").upsert(data, on_conflict="id").execute()
    except Exception as e:
        logger.error("خطا در ذخیره تنظیمات بات: %s", e)


async def get_user_settings(user_id: int) -> dict:
    """دریافت تنظیمات کاربر با مقادیر پیش‌فرض"""
    saved = await asyncio.to_thread(_db_get_user_settings, user_id)
    settings = DEFAULT_USER_SETTINGS.copy()
    settings.update(saved)
    return settings


async def save_user_setting(user_id: int, key: str, value):
    """ذخیره یک تنظیم کاربر"""
    current = await asyncio.to_thread(_db_get_user_settings, user_id)
    current[key] = value
    await asyncio.to_thread(_db_save_user_settings, user_id, current)


def _db_get_group_stats(chat_title: str) -> dict:
    """آمار یک گروه"""
    try:
        # تعداد کل پیام‌ها
        total = supabase.table("telegram_updates").select(
            "id", count="exact"
        ).eq("chat_title", chat_title).execute()
        
        # پیام‌های ۷ روز اخیر
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        weekly = supabase.table("telegram_updates").select(
            "id", count="exact"
        ).eq("chat_title", chat_title).gte("date", week_ago).execute()
        
        # پیام‌های ۳۰ روز اخیر  
        month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        monthly = supabase.table("telegram_updates").select(
            "id", count="exact"
        ).eq("chat_title", chat_title).gte("date", month_ago).execute()
        
        return {
            "total": total.count or 0,
            "weekly": weekly.count or 0,
            "monthly": monthly.count or 0,
        }
    except Exception as e:
        logger.error("خطا در آمار گروه: %s", e)
        return {"total": 0, "weekly": 0, "monthly": 0}


def _db_get_group_messages(chat_title: str, days: int = 7, limit: int = 500) -> list:
    """دریافت پیام‌های یک گروه در بازه زمانی مشخص"""
    try:
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        res = supabase.table("telegram_updates").select(
            "text, first_name, username, date"
        ).eq("chat_title", chat_title).gte("date", since).order(
            "date", desc=True
        ).limit(limit).execute()
        return res.data or []
    except Exception as e:
        logger.error("خطا در دریافت پیام‌های گروه: %s", e)
        return []


async def generate_ai_report(chat_title: str, messages: list, report_type: str, lang: str = "fa") -> str:
    """تولید گزارش با استفاده از OpenAI GPT"""
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API key is not configured." if lang == "en" else "⚠️ کلید API هوش مصنوعی تنظیم نشده است."
    
    if not messages:
        if lang == "en":
            period = "week" if report_type == "weekly" else "month"
            return f"📭 No messages found in this group in the past {period}."
        else:
            period = "هفته" if report_type == "weekly" else "ماه"
            return f"📭 هیچ پیامی در {period} گذشته در این گروه یافت نشد."
    
    # آماده‌سازی متن پیام‌ها برای GPT
    messages_text = []
    for msg in messages[:200]:  # حداکثر 200 پیام
        text = msg.get("text", "")
        if text and len(text) > 5:  # فقط پیام‌های معنادار
            sender = msg.get("first_name") or msg.get("username") or ("Unknown" if lang == "en" else "ناشناس")
            messages_text.append(f"- {sender}: {text[:200]}")
    
    if not messages_text:
        return "📭 No analyzable text messages found." if lang == "en" else "📭 پیام متنی قابل تحلیلی یافت نشد."
    
    if lang == "en":
        period_text = "past week" if report_type == "weekly" else "past month"
        prompt = f"""You are an intelligent analyst. Please analyze the following messages from the Telegram group "{chat_title}" from the {period_text} and provide a concise and useful summary report in English.

The report should include:
1. 📌 General summary of group activity
2. 🔥 Hot and frequent topics
3. 👥 Level of interaction and participation
4. 💡 Key points and highlights
5. 📊 General statistics (Message count: {len(messages)})

Messages:
{chr(10).join(messages_text[:100])}

Write a short, concise and readable report (max 500 words)."""
        system_msg = "You are a professional Telegram group analyst who provides concise and useful reports in English."
        report_header = f"📊 {period_text.title()} Report for \"{chat_title}\":"
    else:
        period_text = "هفته گذشته" if report_type == "weekly" else "ماه گذشته"
        prompt = f"""شما یک تحلیلگر هوشمند هستید. لطفاً پیام‌های زیر از گروه تلگرامی "{chat_title}" در {period_text} را تحلیل کنید و یک گزارش خلاصه و کاربردی به فارسی ارائه دهید.

گزارش باید شامل موارد زیر باشد:
1. 📌 خلاصه کلی فعالیت گروه
2. 🔥 موضوعات داغ و پرتکرار
3. 👥 میزان تعامل و مشارکت
4. 💡 نکات کلیدی و مهم
5. 📊 آمار کلی (تعداد پیام: {len(messages)})

پیام‌ها:
{chr(10).join(messages_text[:100])}

گزارش را کوتاه، خلاصه و خوانا بنویسید (حداکثر 500 کلمه)."""
        system_msg = "شما یک تحلیلگر حرفه‌ای گروه‌های تلگرامی هستید که گزارش‌های خلاصه و کاربردی به زبان فارسی ارائه می‌دهید."
        report_header = f"📊 گزارش {period_text} گروه «{chat_title}»:"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                report = data["choices"][0]["message"]["content"]
                return f"{report_header}\n\n{report}"
            else:
                logger.error("خطا در OpenAI API: %s", response.text)
                return "❌ خطا در تولید گزارش. لطفاً دوباره تلاش کنید."

    except Exception as e:
        logger.error("خطا در تولید گزارش AI: %s", e)
        return "❌ خطا در اتصال به سرویس هوش مصنوعی."


# ─────────────────────────────────────────────────────────────────
#  کمکی‌های ادمین
# ─────────────────────────────────────────────────────────────────

async def is_admin_telegram_user(tg_user) -> bool:
    username = tg_user.username
    norm = normalize_username(username)
    if norm == "omiddshojaei":
        return True
    user_row = await fetch_allowed_user(username)
    if not user_row:
        return False
    return get_user_effective_role(user_row) in ("owner", "admin")


def extract_user_identity_from_message(msg) -> tuple:
    norm_username = None
    user_id = None
    
    is_forwarded = bool(
        getattr(msg, "forward_from", None) or
        getattr(msg, "forward_from_chat", None) or
        getattr(msg, "forward_sender_name", None) or
        getattr(msg, "forward_origin", None)
    )
    
    contact = getattr(msg, "contact", None)
    if contact:
        if getattr(contact, "user_id", None):
            user_id = contact.user_id
        if getattr(contact, "username", None):
            norm_username = normalize_username(contact.username)
    
    if user_id is None:
        fwd = getattr(msg, "forward_from", None)
        if fwd:
            user_id = getattr(fwd, "id", None)
            if getattr(fwd, "username", None):
                norm_username = normalize_username(fwd.username)
    
    if user_id is None and norm_username is None:
        fwd_origin = getattr(msg, "forward_origin", None)
        if fwd_origin:
            try:
                sender = getattr(fwd_origin, "sender_user", None)
                if sender:
                    user_id = getattr(sender, "id", None)
                    if getattr(sender, "username", None):
                        norm_username = normalize_username(sender.username)
            except Exception:
                pass
    
    text = (getattr(msg, "text", None) or "").strip()
    if not is_forwarded and text and norm_username is None and user_id is None:
        stripped = text.lstrip("@")
        if stripped.isdigit():
            user_id = int(stripped)
        else:
            norm_username = normalize_username(text)
    
    return norm_username, user_id


# ─────────────────────────────────────────────────────────────────
#  سازنده کیبوردها
# ─────────────────────────────────────────────────────────────────

def build_admin_main_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("user_management", lang), callback_data="admin|access")],
        [InlineKeyboardButton(t("search_user", lang), callback_data="admin|search")],
        [InlineKeyboardButton(t("group_management", lang), callback_data="admin|groups")],
        [InlineKeyboardButton(t("reports", lang), callback_data="admin|reports")],
        [InlineKeyboardButton(t("audit_log", lang), callback_data="admin|audit")],
        [InlineKeyboardButton(t("settings", lang), callback_data="admin|settings")],
    ])


def build_role_list_keyboard(counts: dict, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"👑 مالک ({counts.get('owner', 0)})", callback_data="admin|role|owner|0")],
        [InlineKeyboardButton(f"🛡 ادمین ({counts.get('admin', 0)})", callback_data="admin|role|admin|0")],
        [InlineKeyboardButton(f"👤 کاربر ({counts.get('user', 0)})", callback_data="admin|role|user|0")],
        [InlineKeyboardButton(f"🚫 مسدود ({counts.get('blocked', 0)})", callback_data="admin|role|blocked|0")],
        [InlineKeyboardButton(t("back", lang), callback_data="admin|back")],
    ])


def build_report_type_keyboard(chat_title: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 هفتگی", callback_data=f"report|weekly|{chat_title}"),
            InlineKeyboardButton("📆 ماهانه", callback_data=f"report|monthly|{chat_title}"),
        ],
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel")],
    ])


def build_back_keyboard(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=callback)]])


def build_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ انصراف", callback_data="cancel")]])


def build_user_settings_keyboard(settings: dict, lang: str = None) -> InlineKeyboardMarkup:
    """کیبورد تنظیمات کاربر"""
    if lang is None:
        lang = settings.get("language", "fa")
    notif = settings.get("notifications", True)
    date_fmt = settings.get("date_format", "shamsi")
    page_size = settings.get("page_size", 5)
    auto_report = settings.get("auto_report", False)
    
    lang_text = LANGUAGE_OPTIONS.get(settings.get("language", "fa"), "fa")
    date_text = t("date_shamsi", lang) if date_fmt == "shamsi" else t("date_miladi", lang)
    notif_text = f"🔔 {t('notif_on', lang)}" if notif else f"🔕 {t('notif_off', lang)}"
    auto_text = f"✅ {t('auto_report_on', lang)}" if auto_report else f"❌ {t('auto_report_off', lang)}"
    
    # لیبل‌های دکمه‌ها
    lang_label = "🌐 Language" if lang == "en" else "🌐 زبان"
    notif_label = "🔔 Notifications" if lang == "en" else "🔔 نوتیفیکیشن"
    date_label = "📅 Date Format" if lang == "en" else "📅 فرمت تاریخ"
    page_label = "📄 Page Size" if lang == "en" else "📄 تعداد در صفحه"
    auto_label = "📊 Auto Report" if lang == "en" else "📊 گزارش خودکار"
    back_label = "🔙 Back" if lang == "en" else "🔙 بازگشت"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{notif_label}: {notif_text}", callback_data="settings|notifications")],
        [InlineKeyboardButton(f"{date_label}: {date_text}", callback_data="settings|date_format")],
        [InlineKeyboardButton(f"{page_label}: {page_size}", callback_data="settings|page_size")],
        [InlineKeyboardButton(f"{auto_label}: {auto_text}", callback_data="settings|auto_report")],
        [InlineKeyboardButton(back_label, callback_data="settings|back")],
    ])


def build_admin_settings_keyboard(bot_settings: dict) -> InlineKeyboardMarkup:
    """کیبورد تنظیمات ادمین"""
    welcome_msg = bot_settings.get("welcome_message", "پیام پیش‌فرض")
    default_lang = bot_settings.get("default_language", "fa")
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ پیام خوش‌آمدگویی", callback_data="admin|settings|welcome")],
        [InlineKeyboardButton("📊 تنظیمات گزارش", callback_data="admin|settings|reports")],
        [InlineKeyboardButton("🔔 تنظیمات نوتیفیکیشن", callback_data="admin|settings|notif")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin|back")],
    ])


def build_pagination_keyboard(items: list, page: int, callback_prefix: str, 
                               item_callback: str, back_callback: str) -> InlineKeyboardMarkup:
    """ساخت کیبورد با صفحه‌بندی"""
    total_pages = (len(items) + PAGE_SIZE - 1) // PAGE_SIZE
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(items))
    
    buttons = []
    for item in items[start:end]:
        if isinstance(item, dict):
            label = item.get("label", str(item.get("id", "?")))
            item_id = item.get("id")
        else:
            label = str(item)
            item_id = item
        buttons.append([InlineKeyboardButton(label, callback_data=f"{item_callback}|{item_id}")])
    
    # دکمه‌های ناوبری
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"{callback_prefix}|{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"{callback_prefix}|{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data=back_callback)])
    
    return InlineKeyboardMarkup(buttons)


# ─────────────────────────────────────────────────────────────────
#  هندلرها
# ─────────────────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    asyncio.create_task(queue_log(update))
    await clear_pending_mode(update.effective_user.id)

    user = update.effective_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    # دریافت زبان کاربر
    settings = await get_user_settings(user.id)
    lang = settings.get("language", "fa")
    
    await update.effective_chat.send_message(
        t("hello", lang, name=full_name or "Friend"),
        reply_markup=MAIN_REPLY_KEYBOARD
    )
    
    if await is_admin_telegram_user(user):
        await update.effective_chat.send_message(
            t("admin_menu", lang),
            reply_markup=build_admin_main_keyboard(lang)
        )


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر /cancel"""
    if update.effective_chat.type != "private":
        return

    tg_user = update.effective_user
    await clear_pending_mode(tg_user.id)
    
    settings = await get_user_settings(tg_user.id)
    lang = settings.get("language", "fa")
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t("operation_cancelled", lang),
        reply_markup=MAIN_REPLY_KEYBOARD
    )


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر پروفایل کاربر"""
    if update.effective_chat.type != "private":
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id

    settings = await get_user_settings(tg_user.id)
    lang = settings.get("language", "fa")

    if not tg_user.username:
        await context.bot.send_message(
            chat_id=chat_id,
            text=t("need_username", lang)
        )
        return

    allowed = await fetch_allowed_user(tg_user.username)
    
    full_name = f"{tg_user.first_name or '-'} {tg_user.last_name or ''}".strip()

    if not allowed:
        not_allowed_text = "⚠️ You are not in the allowed users list." if lang == "en" else "⚠️ شما در لیست کاربران مجاز نیستید."
        await context.bot.send_message(
            chat_id=chat_id,
            text=t("your_profile", lang, name=full_name, id=tg_user.id, username=tg_user.username, role="-") + f"\n\n{not_allowed_text}"
        )
        return

    role = get_user_effective_role(allowed)
    groups = await get_accessible_groups_for_user(allowed)
    
    role_icon = ROLE_ICONS.get(role, "")
    role_label = ROLE_LABELS.get(role, role)
    
    groups_label = "Groups" if lang == "en" else "تعداد گروه‌ها"
    your_groups_label = "Your groups" if lang == "en" else "گروه‌های شما"
    
    text = t("your_profile", lang, name=full_name, id=tg_user.id, username=tg_user.username, role=f"{role_icon} {role_label}")
    text += f"\n📊 {groups_label}: {len(groups)}\n"
    
    if groups:
        text += f"\n💬 {your_groups_label}:\n"
        for i, g in enumerate(groups[:10], 1):
            text += f"  {i}. {g}\n"
        if len(groups) > 10:
            text += f"  ... و {len(groups) - 10} گروه دیگر"
    
    await context.bot.send_message(chat_id=chat_id, text=text)


async def groups_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    asyncio.create_task(queue_log(update))

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    
    if not tg_user.username:
        await context.bot.send_message(
            chat_id=chat_id,
            text="برای استفاده از بات باید username تلگرام داشته باشید."
        )
        return

    allowed = await fetch_allowed_user(tg_user.username)
    
    if not allowed:
        await context.bot.send_message(chat_id=chat_id, text="شما در لیست کاربران مجاز نیستید.")
        return
    
    if get_user_effective_role(allowed) == "blocked":
        await context.bot.send_message(chat_id=chat_id, text="دسترسی شما مسدود شده است.")
        return
    
    groups = await get_accessible_groups_for_user(allowed)
    
    if not groups:
        await context.bot.send_message(chat_id=chat_id, text="هیچ گروهی برای شما ثبت نشده.")
        return
    
    await set_pending_mode(tg_user.id, "await_group_number")
    
    lines = [f"{i+1}. {t}" for i, t in enumerate(groups)]
    await context.bot.send_message(
        chat_id=chat_id,
        text="گروه‌های شما:\n\n" + "\n".join(lines) + "\n\nشماره گروه را ارسال کنید یا /cancel برای انصراف.",
        reply_markup=build_cancel_keyboard()
    )


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    text = (update.message.text or "").strip()

    # دکمه‌های منو
    if text == BUTTON_HOME:
        await start_handler(update, context)
        return

    if text == BUTTON_GROUPS:
        await groups_handler(update, context)
        return

    if text == BUTTON_PROFILE:
        await profile_handler(update, context)
        return
    
    if text == BUTTON_CANCEL:
        await cancel_handler(update, context)
        return
    
    if text == BUTTON_REPORTS:
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        
        # بررسی دسترسی کاربر
        if not tg_user.username:
            await context.bot.send_message(
                chat_id=chat_id,
                text=t("need_username", lang)
            )
            return

        allowed = await fetch_allowed_user(tg_user.username)
        if not allowed or get_user_effective_role(allowed) == "blocked":
            await context.bot.send_message(
                chat_id=chat_id,
                text=t("no_access", lang)
            )
            return
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=t("select_report_type", lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("weekly_report", lang), callback_data="rpt|weekly")],
                [InlineKeyboardButton(t("monthly_report", lang), callback_data="rpt|monthly")],
                [InlineKeyboardButton(t("cancel", lang), callback_data="cancel")],
            ])
        )
        return

    if text == BUTTON_SETTINGS:
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        title = "⚙️ Your Settings:\n\nClick on any option to change it." if lang == "en" else "⚙️ تنظیمات شما:\n\nبرای تغییر هر مورد روی آن کلیک کنید."
        await context.bot.send_message(
            chat_id=chat_id,
            text=title,
            reply_markup=build_user_settings_keyboard(settings, lang)
        )
        return

    if text == BUTTON_HELP:
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        await context.bot.send_message(
            chat_id=chat_id,
            text=t("help_text", lang)
        )
        return

    asyncio.create_task(queue_log(update))

    if text.startswith("/"):
        return

    mode = await get_pending_mode(tg_user.id)
    
    # حالت جستجو
    if mode == "await_search_query":
        results = await asyncio.to_thread(_db_search_users, text)
        await clear_pending_mode(tg_user.id)
        
        if not results:
            await context.bot.send_message(
                chat_id=chat_id,
                text="کاربری یافت نشد.",
                reply_markup=build_back_keyboard("admin|back")
            )
            return
        
        buttons = []
        for u in results[:10]:
            username = u.get("telegram_username") or "-"
            norm = normalize_username(username) or username
            role = get_user_effective_role(u)
            label = f"{ROLE_ICONS.get(role, '')} @{norm}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"admin|user|{u.get('id')}")])
        
        buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin|back")])
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔍 نتایج جستجو ({len(results)} کاربر):",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # حالت تنظیم پیام خوش‌آمدگویی
    if mode == "await_welcome_message":
        bot_settings = await asyncio.to_thread(_db_get_bot_settings)
        bot_settings["welcome_message"] = text
        await asyncio.to_thread(_db_save_bot_settings, bot_settings)
        await clear_pending_mode(tg_user.id)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ پیام خوش‌آمدگویی ذخیره شد:\n\n{text}",
            reply_markup=build_back_keyboard("admin|settings")
        )
        return
    
    # حالت افزودن کاربر
    if mode and mode.startswith("await_adduser|"):
        _, role_key = mode.split("|", 1)
        norm_username, user_id = extract_user_identity_from_message(update.message)

        if norm_username is None and user_id is None:
            await context.bot.send_message(
                chat_id=chat_id,
                text="نتوانستم کاربر را شناسایی کنم.\nیوزرنیم، آیدی، فوروارد یا Contact ارسال کنید.",
                reply_markup=build_cancel_keyboard()
            )
            return

        existing = None
        if norm_username:
            existing = await fetch_allowed_user(norm_username)
        if not existing and user_id:
            existing = await fetch_allowed_user_by_id(user_id)
        
        if existing:
            await clear_pending_mode(tg_user.id)
            existing_id = existing.get("id")
            existing_role = get_user_effective_role(existing)
            existing_username = existing.get("telegram_username") or "-"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ این کاربر قبلاً ثبت شده.\n\n"
                     f"👤 کاربر: {existing_username}\n"
                     f"🎭 نقش فعلی: {ROLE_ICONS.get(existing_role, '')} {ROLE_LABELS.get(existing_role, existing_role)}\n"
                     f"🎯 نقش جدید: {ROLE_ICONS.get(role_key, '')} {ROLE_LABELS.get(role_key, role_key)}\n\n"
                     f"آیا می‌خواهید سطح دسترسی این کاربر را تغییر دهید؟",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ بله، تغییر بده", callback_data=f"admin|setrole|{role_key}|{existing_id}"),
                        InlineKeyboardButton("❌ خیر", callback_data=f"admin|role|{role_key}|0"),
                    ],
                    [InlineKeyboardButton("🏠 منوی ادمین", callback_data="admin|back")],
                ])
            )
            return

        insert_data = {"role": role_key}
        if norm_username:
            insert_data["telegram_username"] = f"@{norm_username}"
        if user_id:
            insert_data["telegram_user_id"] = user_id

        if role_key == "blocked":
            insert_data.update({"is_admin": False, "is_active": False})
        elif role_key in ("owner", "admin"):
            insert_data.update({"is_admin": True, "is_active": True})
        else:
            insert_data.update({"is_admin": False, "is_active": True})
        
        try:
            await asyncio.to_thread(_db_insert_user, insert_data)
            user_cache.clear()
            
            # ثبت در Audit Log
            await log_audit(
                "ADD_USER",
                tg_user.username or str(tg_user.id),
                norm_username or str(user_id),
                {"role": role_key}
            )
        except Exception as e:
            logger.error("خطا در افزودن کاربر: %s", e)
            await context.bot.send_message(chat_id=chat_id, text="خطا در افزودن کاربر.")
            await clear_pending_mode(tg_user.id)
            return

        await clear_pending_mode(tg_user.id)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ کاربر با نقش {ROLE_LABELS.get(role_key, role_key)} اضافه شد.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin|role|{role_key}|0")],
                [InlineKeyboardButton("🏠 منوی ادمین", callback_data="admin|back")],
            ])
        )
        return

    if not mode:
        await context.bot.send_message(
            chat_id=chat_id,
            text="از منو استفاده کنید یا /groups را بفرستید."
        )
        return

    # انتخاب شماره گروه
    if mode == "await_group_number":
        if not text.isdigit():
            await context.bot.send_message(
                chat_id=chat_id,
                text="فقط شماره گروه را ارسال کنید.",
                reply_markup=build_cancel_keyboard()
            )
            return

        idx = int(text) - 1
        allowed = await fetch_allowed_user(tg_user.username)
        
        if not allowed or get_user_effective_role(allowed) == "blocked":
            await context.bot.send_message(chat_id=chat_id, text="دسترسی شما معتبر نیست.")
            await clear_pending_mode(tg_user.id)
            return

        groups = await get_accessible_groups_for_user(allowed)
        
        if not groups or idx < 0 or idx >= len(groups):
            await context.bot.send_message(
                chat_id=chat_id,
                text="شماره نامعتبر است.",
                reply_markup=build_cancel_keyboard()
            )
            return

        chat_title = groups[idx]
        await set_pending_mode(tg_user.id, "await_report_type")

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"گروه «{chat_title}» انتخاب شد.\nنوع گزارش:",
            reply_markup=build_report_type_keyboard(chat_title)
        )
        return

    await context.bot.send_message(chat_id=chat_id, text="از منو استفاده کنید یا /cancel برای لغو.")


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(queue_log(update))

    query = update.callback_query
    await query.answer()

    tg_user = query.from_user
    data = query.data or ""

    # عملیات بدون کار
    if data == "noop":
            return

    # انصراف
    if data == "cancel":
        await clear_pending_mode(tg_user.id)
        await query.edit_message_text("❌ عملیات لغو شد.")
        return

    # بازگشت به منوی اصلی ادمین
    if data == "admin|back":
        if not await is_admin_telegram_user(tg_user):
            await query.edit_message_text(t("no_admin", "fa"))
            return
        await clear_pending_mode(tg_user.id)
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        await query.edit_message_text(t("admin_menu", lang), reply_markup=build_admin_main_keyboard(lang))
        return

    # انتخاب نوع گزارش (هفتگی/ماهانه)
    if data.startswith("rpt|"):
        report_type = data.split("|")[1]  # weekly or monthly
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        
        allowed = await fetch_allowed_user(tg_user.username)
        if not allowed or get_user_effective_role(allowed) == "blocked":
            await query.edit_message_text(t("no_access", lang))
            return
        
        groups = await get_accessible_groups_for_user(allowed)
        
        if not groups:
            await query.edit_message_text(t("no_groups", lang))
            return
        
        period = t("report_weekly", lang) if report_type == "weekly" else t("report_monthly", lang)
        
        # نمایش لیست گروه‌ها با صفحه‌بندی
        buttons = []
        for g in groups[:15]:  # حداکثر 15 گروه در یک صفحه
            buttons.append([InlineKeyboardButton(
                f"💬 {g[:30]}",
                callback_data=f"genrpt|{report_type}|{g[:50]}"
            )])
        
        buttons.append([InlineKeyboardButton(t("back", lang), callback_data="cancel")])
        
        await query.edit_message_text(
            f"📊 {period}\n\n{t('select_group', lang)}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # تولید گزارش برای گروه انتخاب شده
    if data.startswith("genrpt|"):
        parts = data.split("|", 2)
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        
        if len(parts) != 3:
            await query.edit_message_text(t("error", lang))
            return
        
        _, report_type, chat_title = parts
        
        allowed = await fetch_allowed_user(tg_user.username)
        if not allowed or get_user_effective_role(allowed) == "blocked":
            await query.edit_message_text(t("no_access", lang))
            return
        
        # بررسی دسترسی به گروه
        user_groups = await get_accessible_groups_for_user(allowed)
        if chat_title not in user_groups:
            await query.edit_message_text(t("no_access", lang))
            return
        
        period = t("report_weekly", lang) if report_type == "weekly" else t("report_monthly", lang)
        days = 7 if report_type == "weekly" else 30
        
        # پیام در حال تولید
        generating_text = f"⏳ Generating {period} report for \"{chat_title}\"...\n\n🤖 AI is analyzing messages..." if lang == "en" else f"⏳ در حال تولید گزارش {period} گروه «{chat_title}»...\n\n🤖 هوش مصنوعی در حال تحلیل پیام‌ها است..."
        await query.edit_message_text(generating_text)
        
        # دریافت پیام‌ها و تولید گزارش
        messages = await asyncio.to_thread(_db_get_group_messages, chat_title, days)
        report = await generate_ai_report(chat_title, messages, report_type, lang)
        
        # ارسال گزارش
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=report,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t("another_report", lang), callback_data=f"rpt|{report_type}")],
                [InlineKeyboardButton(t("home", lang), callback_data="cancel")],
            ])
        )
        return

    # گزارش قدیمی (سازگاری با قبل)
    if data.startswith("report|"):
        parts = data.split("|", 2)
        if len(parts) != 3:
            await query.edit_message_text("درخواست نامعتبر.")
            await clear_pending_mode(tg_user.id)
            return

        _, mode, chat_title = parts
        allowed = await fetch_allowed_user(tg_user.username)
        
        if not allowed or get_user_effective_role(allowed) == "blocked":
            await query.edit_message_text("دسترسی شما معتبر نیست.")
            await clear_pending_mode(tg_user.id)
            return

        days = 7 if mode == "weekly" else 30
        
        await query.edit_message_text("⏳ در حال تولید گزارش...")
        
        messages = await asyncio.to_thread(_db_get_group_messages, chat_title, days)
        report = await generate_ai_report(chat_title, messages, mode)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=report
        )
        await clear_pending_mode(tg_user.id)
        return

    # منوهای ادمین
    if data.startswith("admin|"):
        logger.info(f"ADMIN callback: data={data}")
        if not await is_admin_telegram_user(tg_user):
            await query.edit_message_text("دسترسی ادمین ندارید.")
            return

        parts = data.split("|")
        logger.info(f"ADMIN parts: {parts}, len={len(parts)}")

        # لیست نقش‌ها
        if data == "admin|access":
            settings = await get_user_settings(tg_user.id)
            lang = settings.get("language", "fa")
            all_users = await asyncio.to_thread(_db_get_all_users)
            counts = {r: 0 for r in ROLE_LEVELS}
            for u in all_users:
                role = get_user_effective_role(u)
                if role in counts:
                    counts[role] += 1
            
            await query.edit_message_text(t("select_role", lang), reply_markup=build_role_list_keyboard(counts, lang))
            return
        
        # جستجو
        if data == "admin|search":
            settings = await get_user_settings(tg_user.id)
            lang = settings.get("language", "fa")
            await set_pending_mode(tg_user.id, "await_search_query")
            await query.edit_message_text(
                t("search_prompt", lang),
                reply_markup=build_cancel_keyboard()
            )
            return

        # کاربران یک نقش با صفحه‌بندی
        if len(parts) == 4 and parts[1] == "role":
            role_key = parts[2]
            try:
                page = int(parts[3])
            except ValueError:
                page = 0
            
            if role_key not in ROLE_LEVELS:
                await query.edit_message_text("نقش نامعتبر.")
                return

            all_users = await asyncio.to_thread(_db_get_all_users)
            filtered = [u for u in all_users if get_user_effective_role(u) == role_key]
            
            if not filtered:
                await query.edit_message_text(
                    f"کاربری با نقش {ROLE_LABELS.get(role_key)} نیست.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ افزودن کاربر", callback_data=f"admin|adduser|{role_key}")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin|access")],
                    ])
                )
                return

            # صفحه‌بندی
            total_pages = (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE
            page = max(0, min(page, total_pages - 1))
            start = page * PAGE_SIZE
            end = min(start + PAGE_SIZE, len(filtered))
            
            buttons = []
            for u in filtered[start:end]:
                username = u.get("telegram_username") or "-"
                norm = normalize_username(username) or username
                label = f"@{norm}" if norm != "-" else "(بدون یوزرنیم)"
                buttons.append([InlineKeyboardButton(label, callback_data=f"admin|user|{u.get('id')}")])
            
            # ناوبری
            nav = []
            if page > 0:
                nav.append(InlineKeyboardButton("◀️", callback_data=f"admin|role|{role_key}|{page-1}"))
            nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                nav.append(InlineKeyboardButton("▶️", callback_data=f"admin|role|{role_key}|{page+1}"))
            if len(nav) > 1:
                buttons.append(nav)
            
            buttons.append([InlineKeyboardButton("➕ افزودن کاربر", callback_data=f"admin|adduser|{role_key}")])
            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin|access")])
            
            await query.edit_message_text(
                f"کاربران {ROLE_LABELS.get(role_key)} ({len(filtered)} نفر):",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        # افزودن کاربر
        if len(parts) == 3 and parts[1] == "adduser":
            role_key = parts[2]
            if role_key not in ROLE_LEVELS:
                await query.edit_message_text("نقش نامعتبر.")
                return

            await set_pending_mode(tg_user.id, f"await_adduser|{role_key}")
            await query.edit_message_text(
                f"➕ افزودن کاربر با نقش {ROLE_LABELS.get(role_key)}:\n\n"
                "یکی از موارد زیر را ارسال کنید:\n"
                "• یوزرنیم (با یا بدون @)\n"
                "• فوروارد پیام از کاربر\n"
                "• آیدی عددی\n"
                "• ارسال Contact",
                reply_markup=build_cancel_keyboard()
            )
            return

        # جزئیات کاربر
        if len(parts) == 3 and parts[1] == "user":
            try:
                db_id = int(parts[2])
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return

            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return

            username = row.get("telegram_username") or "-"
            norm = normalize_username(username) or username
            role = get_user_effective_role(row)
            is_active = row.get("is_active", True)
            tg_id = row.get("telegram_user_id") or "-"
            created = row.get("created_at", "-")[:10] if row.get("created_at") else "-"
            
            text = (
                f"👤 کاربر: @{norm}\n"
                f"🔢 آیدی: {tg_id}\n"
                f"{ROLE_ICONS.get(role, '')} نقش: {ROLE_LABELS.get(role)}\n"
                f"📅 تاریخ ثبت: {created}\n"
                f"وضعیت: {'✅ فعال' if is_active else '🚫 مسدود'}"
            )
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 تغییر نقش", callback_data=f"admin|changerole|{db_id}")],
                    [InlineKeyboardButton("💬 مدیریت گروه‌ها", callback_data=f"admin|usergroups|{db_id}|0")],
                    [InlineKeyboardButton("🗑 حذف", callback_data=f"admin|confirmdelete|{db_id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin|role|{role}|0")],
                ])
            )
            return
        
        # مدیریت گروه‌های کاربر
        if len(parts) >= 3 and parts[1] == "usergroups":
            try:
                db_id = int(parts[2])
                page = int(parts[3]) if len(parts) > 3 else 0
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return
            
            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return
            
            username = row.get("telegram_username") or ""
            user_groups = await asyncio.to_thread(_db_get_user_group_permissions, username)
            user_group_titles = {g.get("chat_title") for g in user_groups}
            
            all_groups = await asyncio.to_thread(_db_get_all_groups)
            all_group_titles = [g.get("chat_title") for g in all_groups if g.get("chat_title")]
            
            total_pages = max(1, (len(all_group_titles) + PAGE_SIZE - 1) // PAGE_SIZE)
            page = max(0, min(page, total_pages - 1))
            start = page * PAGE_SIZE
            end = min(start + PAGE_SIZE, len(all_group_titles))
            
            buttons = []
            for title in all_group_titles[start:end]:
                has_access = title in user_group_titles
                icon = "✅" if has_access else "❌"
                action = "removegroup" if has_access else "addgroup"
                buttons.append([InlineKeyboardButton(
                    f"{icon} {title[:30]}",
                    callback_data=f"admin|{action}|{db_id}|{title[:50]}"
                )])
            
            nav = []
            if page > 0:
                nav.append(InlineKeyboardButton("◀️", callback_data=f"admin|usergroups|{db_id}|{page-1}"))
            nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                nav.append(InlineKeyboardButton("▶️", callback_data=f"admin|usergroups|{db_id}|{page+1}"))
            if len(nav) > 1:
                buttons.append(nav)
            
            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin|user|{db_id}")])
            
            norm = normalize_username(username) or "-"
            await query.edit_message_text(
                f"💬 گروه‌های @{norm}:\n✅ = دسترسی دارد | ❌ = دسترسی ندارد",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        
        # اضافه کردن گروه به کاربر
        if len(parts) == 4 and parts[1] == "addgroup":
            try:
                db_id = int(parts[2])
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return
            
            chat_title = parts[3]
            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return
            
            username = row.get("telegram_username") or ""
            await asyncio.to_thread(_db_add_user_group_permission, username, chat_title)
            groups_cache.clear()
            
            await log_audit(
                "ADD_USER_GROUP",
                tg_user.username or str(tg_user.id),
                f"{username} -> {chat_title}",
                {}
            )
            
            # بروزرسانی لیست گروه‌ها
            user_groups = await asyncio.to_thread(_db_get_user_group_permissions, username)
            user_group_titles = {g.get("chat_title") for g in user_groups}
            all_groups = await asyncio.to_thread(_db_get_all_groups)
            all_group_titles = [g.get("chat_title") for g in all_groups if g.get("chat_title")]
            
            buttons = []
            for title in all_group_titles[:PAGE_SIZE]:
                has_access = title in user_group_titles
                icon = "✅" if has_access else "❌"
                action = "removegroup" if has_access else "addgroup"
                buttons.append([InlineKeyboardButton(
                    f"{icon} {title[:30]}",
                    callback_data=f"admin|{action}|{db_id}|{title[:50]}"
                )])
            
            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin|user|{db_id}")])
            
            norm = normalize_username(username) or "-"
            await query.edit_message_text(
                f"💬 گروه‌های @{norm}:\n✅ = دسترسی دارد | ❌ = دسترسی ندارد",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        # حذف گروه از کاربر
        if len(parts) == 4 and parts[1] == "removegroup":
            try:
                db_id = int(parts[2])
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return
            
            chat_title = parts[3]
            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return
            
            username = row.get("telegram_username") or ""
            await asyncio.to_thread(_db_remove_user_group_permission, username, chat_title)
            groups_cache.clear()
            
            await log_audit(
                "REMOVE_USER_GROUP",
                tg_user.username or str(tg_user.id),
                f"{username} -> {chat_title}",
                {}
            )
            
            # بروزرسانی لیست گروه‌ها
            user_groups = await asyncio.to_thread(_db_get_user_group_permissions, username)
            user_group_titles = {g.get("chat_title") for g in user_groups}
            all_groups = await asyncio.to_thread(_db_get_all_groups)
            all_group_titles = [g.get("chat_title") for g in all_groups if g.get("chat_title")]
            
            buttons = []
            for title in all_group_titles[:PAGE_SIZE]:
                has_access = title in user_group_titles
                icon = "✅" if has_access else "❌"
                action = "removegroup" if has_access else "addgroup"
                buttons.append([InlineKeyboardButton(
                    f"{icon} {title[:30]}",
                    callback_data=f"admin|{action}|{db_id}|{title[:50]}"
                )])
            
            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin|user|{db_id}")])
            
            norm = normalize_username(username) or "-"
            await query.edit_message_text(
                f"💬 گروه‌های @{norm}:\n✅ = دسترسی دارد | ❌ = دسترسی ندارد",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        
        # تغییر نقش
        if len(parts) == 3 and parts[1] == "changerole":
            try:
                db_id = int(parts[2])
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return

            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return
            
            buttons = [
                [InlineKeyboardButton(f"{ROLE_ICONS[r]} {ROLE_LABELS[r]}", callback_data=f"admin|setrole|{r}|{db_id}")]
                for r in ["owner", "admin", "supervisor", "user", "blocked"]
            ]
            buttons.append([InlineKeyboardButton("❌ انصراف", callback_data=f"admin|user|{db_id}")])
            
            await query.edit_message_text("انتخاب نقش جدید:", reply_markup=InlineKeyboardMarkup(buttons))
            return
        
        # تایید حذف
        if len(parts) == 3 and parts[1] == "confirmdelete":
            try:
                db_id = int(parts[2])
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return
            
            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return

            username = row.get("telegram_username") or "-"
            norm = normalize_username(username) or username
            role = get_user_effective_role(row)
            
            await query.edit_message_text(
                f"⚠️ آیا از حذف کاربر @{norm} مطمئن هستید؟\n\nاین عملیات قابل بازگشت نیست!",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ بله، حذف شود", callback_data=f"admin|deleteuser|{db_id}"),
                        InlineKeyboardButton("❌ خیر", callback_data=f"admin|user|{db_id}"),
                    ],
                ])
            )
            return

        # حذف کاربر
        if len(parts) == 3 and parts[1] == "deleteuser":
            try:
                db_id = int(parts[2])
            except ValueError:
                await query.edit_message_text("شناسه نامعتبر.")
                return

            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await query.edit_message_text("کاربر یافت نشد.")
                return

            username = row.get("telegram_username") or "-"
            role = get_user_effective_role(row)

            try:
                await asyncio.to_thread(_db_delete_user, db_id)
                user_cache.clear()
                
                await log_audit(
                    "DELETE_USER",
                    tg_user.username or str(tg_user.id),
                    username,
                    {"role": role}
                )
            except Exception as e:
                logger.error("خطا در حذف: %s", e)
                await query.edit_message_text("خطا در حذف کاربر.")
                return

            await query.edit_message_text(
                "✅ کاربر حذف شد.",
                reply_markup=build_back_keyboard(f"admin|role|{role}|0")
            )
            return

        # تنظیم نقش
        if len(parts) == 4 and parts[1] == "setrole":
            logger.info(f"SETROLE: callback_data={data}, parts={parts}")
            new_role = parts[2]
            try:
                db_id = int(parts[3])
            except ValueError as e:
                logger.error(f"SETROLE ValueError: {e}, parts[3]={parts[3]}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="شناسه نامعتبر."
                )
                return

            if new_role not in ROLE_LEVELS:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="نقش نامعتبر."
                )
                return

            row = await asyncio.to_thread(_db_get_user_by_db_id, db_id)
            if not row:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="کاربر یافت نشد."
                )
                return
                
            old_role = get_user_effective_role(row)
            username = row.get("telegram_username", "-")
            
            update_data = {"role": new_role}
            if new_role in ("owner", "admin"):
                update_data.update({"is_admin": True, "is_active": True})
            elif new_role == "blocked":
                update_data.update({"is_admin": False, "is_active": False})
            else:
                update_data.update({"is_admin": False, "is_active": True})
            
            try:
                await asyncio.to_thread(_db_update_user, db_id, update_data)
                user_cache.clear()
                
                await log_audit(
                    "CHANGE_ROLE",
                    tg_user.username or str(tg_user.id),
                    username,
                    {"old_role": old_role, "new_role": new_role}
                )
            except Exception as e:
                logger.error("خطا در تغییر نقش: %s", e)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ خطا در تغییر نقش."
            )
            return

            # پاسخ به callback
            try:
                await query.answer("✅ نقش تغییر کرد!")
            except:
                pass
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ نقش کاربر {username} به {ROLE_ICONS.get(new_role, '')} {ROLE_LABELS.get(new_role)} تغییر کرد.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت به لیست", callback_data=f"admin|role|{new_role}|0")],
                    [InlineKeyboardButton("🏠 منوی ادمین", callback_data="admin|back")],
                ])
            )
            return

        # گروه‌ها با آمار
        if data == "admin|groups":
            groups = await asyncio.to_thread(_db_get_all_groups)
            if not groups:
                await query.edit_message_text("گروهی ثبت نشده.", reply_markup=build_back_keyboard("admin|back"))
                return

            buttons = []
            for g in groups[:15]:
                title = g.get("chat_title", "?")
                buttons.append([InlineKeyboardButton(f"💬 {title[:35]}", callback_data=f"admin|groupstats|{title[:50]}")])

            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin|back")])

            await query.edit_message_text(
                f"📚 گروه‌ها ({len(groups)} گروه):\nبرای مشاهده آمار روی گروه کلیک کنید.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        # آمار گروه
        if len(parts) == 3 and parts[1] == "groupstats":
            chat_title = parts[2]
            stats = await asyncio.to_thread(_db_get_group_stats, chat_title)
            
            text = (
                f"📊 آمار گروه «{chat_title}»:\n\n"
                f"📨 کل پیام‌ها: {stats['total']:,}\n"
                f"📅 ۷ روز اخیر: {stats['weekly']:,}\n"
                f"📆 ۳۰ روز اخیر: {stats['monthly']:,}\n"
            )
            
            await query.edit_message_text(text, reply_markup=build_back_keyboard("admin|groups"))
            return
        
        # گزارش‌ها
        if data == "admin|reports":
            await query.edit_message_text(
                "📊 گزارش‌ها:\n\nبرای دریافت گزارش از منوی گروه‌ها اقدام کنید.",
                reply_markup=build_back_keyboard("admin|back")
            )
            return

        # تنظیمات
        if data == "admin|settings":
            bot_settings = await asyncio.to_thread(_db_get_bot_settings)
            await query.edit_message_text(
                "⚙️ تنظیمات کلی بات:\n\nبرای تغییر هر مورد روی آن کلیک کنید.",
                reply_markup=build_admin_settings_keyboard(bot_settings)
            )
            return

        # تنظیمات ادمین - پیام خوش‌آمدگویی
        if data == "admin|settings|welcome":
            await set_pending_mode(tg_user.id, "await_welcome_message")
            bot_settings = await asyncio.to_thread(_db_get_bot_settings)
            current = bot_settings.get("welcome_message", "سلام {name} 👋")
            await query.edit_message_text(
                f"✏️ پیام خوش‌آمدگویی فعلی:\n\n{current}\n\n"
                "پیام جدید را ارسال کنید.\n"
                "از {{name}} برای نام کاربر استفاده کنید.",
                reply_markup=build_cancel_keyboard()
            )
            return
        
        # تنظیمات گزارش
        if data == "admin|settings|reports":
            await query.edit_message_text(
                "📊 تنظیمات گزارش:\n\n"
                "• گزارش خودکار هفتگی\n"
                "• گزارش خودکار ماهانه\n"
                "• زمان ارسال گزارش\n\n"
                "این بخش در حال توسعه است.",
                reply_markup=build_back_keyboard("admin|settings")
            )
            return
        
        # تنظیمات نوتیفیکیشن ادمین
        if data == "admin|settings|notif":
            await query.edit_message_text(
                "🔔 تنظیمات نوتیفیکیشن:\n\n"
                "• اطلاع‌رسانی کاربر جدید\n"
                "• اطلاع‌رسانی درخواست گزارش\n"
                "• اطلاع‌رسانی خطاها\n\n"
                "این بخش در حال توسعه است.",
                reply_markup=build_back_keyboard("admin|settings")
            )
            return

        # Audit Log
        if data == "admin|audit":
            logs = await asyncio.to_thread(_db_get_audit_logs, 15)
            
            if not logs:
                await query.edit_message_text(
                    "📄 هیچ لاگی ثبت نشده.",
                    reply_markup=build_back_keyboard("admin|back")
                )
                return

            lines = ["📄 آخرین تغییرات:\n"]
            for log in logs:
                action = log.get("action", "?")
                actor = log.get("actor_username", "?")
                target = log.get("target_info", "?")
                created = log.get("created_at", "")[:16].replace("T", " ") if log.get("created_at") else "-"
                
                action_icons = {
                    "ADD_USER": "➕",
                    "DELETE_USER": "🗑",
                    "CHANGE_ROLE": "🔄",
                    "ADD_USER_GROUP": "✅",
                    "REMOVE_USER_GROUP": "❌",
                }
                icon = action_icons.get(action, "📝")
                
                lines.append(f"{icon} {action}\n   👤 {actor} → {target}\n   🕐 {created}")
            
            await query.edit_message_text(
                "\n".join(lines),
                reply_markup=build_back_keyboard("admin|back")
            )
        return

        await query.edit_message_text("درخواست نامعتبر.")
        return
    
    # تنظیمات کاربر
    if data.startswith("settings|"):
        parts = data.split("|")
        
        # بازگشت به منوی تنظیمات
        if data == "settings|back":
            await clear_pending_mode(tg_user.id)
            await query.edit_message_text("عملیات لغو شد.")
            return
        
        # تغییر نوتیفیکیشن
        if data == "settings|notifications":
            settings = await get_user_settings(tg_user.id)
            current = settings.get("notifications", True)
            await query.edit_message_text(
                f"🔔 نوتیفیکیشن:\n\nوضعیت فعلی: {'روشن' if current else 'خاموش'}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔔 روشن", callback_data="setnotif|on")],
                    [InlineKeyboardButton("🔕 خاموش", callback_data="setnotif|off")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="settings|main")],
                ])
            )
            return
        
        # تغییر فرمت تاریخ
        if data == "settings|date_format":
            await query.edit_message_text(
                "📅 فرمت تاریخ:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("☀️ شمسی", callback_data="setdate|shamsi")],
                    [InlineKeyboardButton("📅 میلادی", callback_data="setdate|miladi")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="settings|main")],
                ])
            )
            return
        
        # تغییر تعداد در صفحه
        if data == "settings|page_size":
            await query.edit_message_text(
                "📄 تعداد آیتم در هر صفحه:",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("5", callback_data="setpage|5"),
                        InlineKeyboardButton("10", callback_data="setpage|10"),
                    ],
                    [
                        InlineKeyboardButton("15", callback_data="setpage|15"),
                        InlineKeyboardButton("20", callback_data="setpage|20"),
                    ],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="settings|main")],
                ])
            )
            return
        
        # تغییر گزارش خودکار
        if data == "settings|auto_report":
            settings = await get_user_settings(tg_user.id)
            current = settings.get("auto_report", False)
            await query.edit_message_text(
                f"📊 گزارش خودکار:\n\nوضعیت فعلی: {'فعال' if current else 'غیرفعال'}\n\n"
                "با فعال کردن این گزینه، گزارش‌های هفتگی به صورت خودکار برای شما ارسال می‌شود.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ فعال", callback_data="setauto|on")],
                    [InlineKeyboardButton("❌ غیرفعال", callback_data="setauto|off")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="settings|main")],
                ])
            )
            return
        
        # برگشت به منوی اصلی تنظیمات
        if data == "settings|main":
            settings = await get_user_settings(tg_user.id)
            lang = settings.get("language", "fa")
            title = "⚙️ Your Settings:\n\nClick on any option to change it." if lang == "en" else "⚙️ تنظیمات شما:\n\nبرای تغییر هر مورد روی آن کلیک کنید."
            await query.edit_message_text(
                title,
                reply_markup=build_user_settings_keyboard(settings, lang)
            )
            return
    
    # اعمال تنظیمات کاربر
    if data.startswith("setnotif|"):
        value = data.split("|")[1] == "on"
        await save_user_setting(tg_user.id, "notifications", value)
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        status = t("notif_on", lang) if value else t("notif_off", lang)
        await query.edit_message_text(
            t("notif_changed", lang, status=status),
            reply_markup=build_user_settings_keyboard(settings, lang)
        )
        return
    
    if data.startswith("setdate|"):
        new_format = data.split("|")[1]
        await save_user_setting(tg_user.id, "date_format", new_format)
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        format_name = t("date_shamsi", lang) if new_format == "shamsi" else t("date_miladi", lang)
        await query.edit_message_text(
            t("date_changed", lang, format=format_name),
            reply_markup=build_user_settings_keyboard(settings, lang)
        )
        return
    
    if data.startswith("setpage|"):
        new_size = int(data.split("|")[1])
        await save_user_setting(tg_user.id, "page_size", new_size)
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        await query.edit_message_text(
            t("page_size_changed", lang, size=new_size),
            reply_markup=build_user_settings_keyboard(settings, lang)
        )
        return
    
    if data.startswith("setauto|"):
        value = data.split("|")[1] == "on"
        await save_user_setting(tg_user.id, "auto_report", value)
        settings = await get_user_settings(tg_user.id)
        lang = settings.get("language", "fa")
        status = t("auto_report_on", lang) if value else t("auto_report_off", lang)
        await query.edit_message_text(
            t("auto_report_changed", lang, status=status),
            reply_markup=build_user_settings_keyboard(settings, lang)
        )
        return
    
    await query.edit_message_text("درخواست شناسایی نشد.")
    await clear_pending_mode(tg_user.id)


# ─────────────────────────────────────────────────────────────────
#  راه‌اندازی
# ─────────────────────────────────────────────────────────────────

async def post_init(app):
    await init_log_queue()
    asyncio.create_task(log_worker())
    logger.info("Bot initialized")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    private_filter = filters.ChatType.PRIVATE & (~filters.COMMAND)

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("cancel", cancel_handler))
    app.add_handler(CommandHandler("groups", groups_handler))
    app.add_handler(CommandHandler("profile", profile_handler))
    app.add_handler(MessageHandler(private_filter, text_message_handler))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
