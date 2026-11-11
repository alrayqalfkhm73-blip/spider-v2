"""Inline Keyboards — أدوات المالك"""
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _ikb(rows: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(rows)


# ═══════════════════════════════════════════════════════════
# 👑 Owner tools (SQL / Python / Read file)
# ═══════════════════════════════════════════════════════════
def owner_tools_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🗄️ تنفيذ SQL", callback_data="owner_tool_sql")],
        [InlineKeyboardButton("🐍 تنفيذ كود بايثون", callback_data="owner_tool_sandbox")],
        [InlineKeyboardButton("📁 قراءة ملف من السيرفر", callback_data="owner_tool_readfile")],
    ])


# ═══════════════════════════════════════════════════════════
# 👤 User info (uinfo)
# ═══════════════════════════════════════════════════════════
def user_info_actions(uid: str) -> InlineKeyboardMarkup:
    u = uid[:25]
    return _ikb([
        [InlineKeyboardButton("👑 ترقية VIP", callback_data=f"uact_vip_{u}"),
         InlineKeyboardButton("💰 نقاط", callback_data=f"uact_pts_{u}")],
        [InlineKeyboardButton("✉️ رسالة", callback_data=f"uact_dm_{u}"),
         InlineKeyboardButton("🚫 حظر", callback_data=f"uact_ban_{u}")],
        [InlineKeyboardButton("🗑️ حذف", callback_data=f"uact_del_{u}"),
         InlineKeyboardButton("📋 سجل", callback_data=f"uact_log_{u}")],
    ])


# ═══════════════════════════════════════════════════════════
# 👑 VIP duration
# ═══════════════════════════════════════════════════════════
def vip_duration(uid: str) -> InlineKeyboardMarkup:
    u = uid[:25]
    return _ikb([
        [InlineKeyboardButton("7 أيام", callback_data=f"vip_set_{u}_7"),
         InlineKeyboardButton("30 يوم", callback_data=f"vip_set_{u}_30")],
        [InlineKeyboardButton("90 يوم", callback_data=f"vip_set_{u}_90"),
         InlineKeyboardButton("♾️ أبدي", callback_data=f"vip_set_{u}_0")],
        [InlineKeyboardButton("❌ إلغاء VIP", callback_data=f"vip_set_{u}_cancel")],
    ])


# ═══════════════════════════════════════════════════════════
# 🚫 Ban duration
# ═══════════════════════════════════════════════════════════
def ban_duration(uid: str) -> InlineKeyboardMarkup:
    u = uid[:25]
    return _ikb([
        [InlineKeyboardButton("24 ساعة", callback_data=f"ban_set_{u}_1"),
         InlineKeyboardButton("7 أيام", callback_data=f"ban_set_{u}_7")],
        [InlineKeyboardButton("30 يوم", callback_data=f"ban_set_{u}_30"),
         InlineKeyboardButton("🚫 دائم", callback_data=f"ban_set_{u}_0")],
        [InlineKeyboardButton("✅ إلغاء الحظر", callback_data=f"ban_unban_{u}")],
    ])


# ═══════════════════════════════════════════════════════════
# 💰 Bulk points
# ═══════════════════════════════════════════════════════════
def bulk_points_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("👥 كل المستخدمين", callback_data="bulk_pts_all")],
        [InlineKeyboardButton("👑 VIP فقط", callback_data="bulk_pts_vip")],
        [InlineKeyboardButton("🆕 جداد (7 أيام)", callback_data="bulk_pts_new")],
        [InlineKeyboardButton("✏️ مخصص (صيغة)", callback_data="bulk_pts_custom")],
    ])


# ═══════════════════════════════════════════════════════════
# 📢 Broadcast
# ═══════════════════════════════════════════════════════════
def broadcast_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("👥 الكل", callback_data="bc_seg_all")],
        [InlineKeyboardButton("👑 VIP فقط", callback_data="bc_seg_vip")],
        [InlineKeyboardButton("🟢 نشطين (7 أيام)", callback_data="bc_seg_active")],
        [InlineKeyboardButton("💰 عندهم نقاط", callback_data="bc_seg_haspoints")],
    ])


# ═══════════════════════════════════════════════════════════
# 🔍 Advanced search
# ═══════════════════════════════════════════════════════════
def advanced_search_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🆔 بـ User ID", callback_data="adv_srch_id")],
        [InlineKeyboardButton("👤 بـ Username", callback_data="adv_srch_username")],
        [InlineKeyboardButton("💰 مدى النقاط", callback_data="adv_srch_points")],
        [InlineKeyboardButton("👑 VIP فقط", callback_data="adv_srch_vip")],
        [InlineKeyboardButton("🚫 محظورين", callback_data="adv_srch_banned")],
    ])


# ═══════════════════════════════════════════════════════════
# ❌ Failed members
# ═══════════════════════════════════════════════════════════
def failed_members_menu(counts: dict = None) -> InlineKeyboardMarkup:
    counts = counts or {}
    total = sum(counts.values())
    return _ikb([
        [InlineKeyboardButton(f"الكل ({total})", callback_data="failed_filter_all"),
         InlineKeyboardButton(f"🔒 Privacy ({counts.get('privacy',0)})", callback_data="failed_filter_privacy")],
        [InlineKeyboardButton(f"💀 Dead ({counts.get('deactivated',0)})", callback_data="failed_filter_deactivated"),
         InlineKeyboardButton(f"⚠️ Other ({counts.get('other',0)})", callback_data="failed_filter_other")],
        [InlineKeyboardButton("🔄 إعادة الكل", callback_data="retry_failed_all"),
         InlineKeyboardButton("📥 CSV", callback_data="export_failed_csv")],
        [InlineKeyboardButton("🗑️ مسح الكل", callback_data="clear_failed")],
    ])


# ═══════════════════════════════════════════════════════════
# 🚫 Blacklist
# ═══════════════════════════════════════════════════════════
def blacklist_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("➕ إضافة يدوياً", callback_data="add_blacklist_manual")],
        [InlineKeyboardButton("🗑️ مسح الكل", callback_data="clear_blacklist")],
    ])


# ═══════════════════════════════════════════════════════════
# 📱 Session picker (general)
# ═══════════════════════════════════════════════════════════
def session_picker(sessions: list = None) -> InlineKeyboardMarkup:
    """sessions: list of {name}"""
    rows = []
    if sessions:
        for s in sessions[:15]:
            rows.append([InlineKeyboardButton(
                f"📱 {s['name'][:40]}",
                callback_data=f"pick_sess_{s['name'][:40]}")])
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 📄 Read file picker
# ═══════════════════════════════════════════════════════════
def read_file_picker(files: list = None) -> InlineKeyboardMarkup:
    """files: list of filenames"""
    rows = []
    if files:
        for f in files[:15]:
            rows.append([InlineKeyboardButton(
                f"📄 {f}", callback_data=f"read_code_{f}")])
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 🗓️ Updates admin
# ═══════════════════════════════════════════════════════════
def updates_admin_menu(updates: list = None) -> InlineKeyboardMarkup:
    """updates: list of {id, title, update_time, published}"""
    rows = []
    if updates:
        for u in updates:
            status = "✅" if u.get("published") else "⏳"
            date_str = (u.get("update_time") or "")[:10]
            title = (u.get("title") or "")[:20]
            rows.append([InlineKeyboardButton(
                f"{status} | {date_str} | {title}...",
                callback_data=f"upd_admin_{u['id']}")])
    return _ikb(rows)


def update_details_menu(uid: int, published: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if published:
        rows.append([InlineKeyboardButton("🔒 إلغاء التفعيل (إخفاء)", callback_data=f"upd_unpublish_{uid}")])
    else:
        rows.append([InlineKeyboardButton("🚀 تفعيل وإرسال للمستخدمين", callback_data=f"upd_publish_{uid}")])
    rows.append([InlineKeyboardButton("🗑️ حذف التحديث نهائياً", callback_data=f"upd_del_{uid}")])
    rows.append([InlineKeyboardButton("↩️ رجوع", callback_data="upd_back")])
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 🎫 Tickets
# ═══════════════════════════════════════════════════════════
def ticket_actions(user_id: str) -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("↩️ رد", callback_data=f"reply_fb_{user_id}"),
         InlineKeyboardButton("✅ إغلاق", callback_data=f"close_ticket_{user_id}")],
    ])


# ═══════════════════════════════════════════════════════════
# 🔨 Auction bid
# ═══════════════════════════════════════════════════════════
def auction_bid(auction_id: int, current_bid: int) -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton(
            f"➕ زايد 50 (يبقى {current_bid+50})",
            callback_data=f"bid_{auction_id}_{current_bid+50}")],
        [InlineKeyboardButton(
            f"➕ زايد 100 (يبقى {current_bid+100})",
            callback_data=f"bid_{auction_id}_{current_bid+100}")],
    ])


# ═══════════════════════════════════════════════════════════
# 🗑️ RAG delete menu
# ═══════════════════════════════════════════════════════════
def rag_delete_menu(docs: list = None) -> InlineKeyboardMarkup:
    """docs: list of doc names"""
    rows = []
    if docs:
        for d in docs[:15]:
            rows.append([InlineKeyboardButton(
                f"🗑️ {d[:40]}",
                callback_data=f"rag_del_{d[:50]}")])
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 📱 Session navigation (pagination)
# ═══════════════════════════════════════════════════════════
def session_nav(page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"ban_pg_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"ban_pg_{page+1}"))
    if nav:
        rows.append(nav)
    return _ikb(rows)
