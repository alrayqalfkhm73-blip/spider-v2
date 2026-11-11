"""Scrape Engine — History Only, Username Only, Batch Auto-Save to DB"""
import asyncio
import time as _time
from database.queries import members as members_q
from database.connection import get_db
from scraper.validators import should_scrape, make_member_tuple, is_blacklisted
from scraper import progress
from logger import get_logger

log = get_logger("scraper.engine")
db = get_db()

async def run_scrape(client, target_chat, owner_id: str, task_id: str,
                     filters: dict = None, cancel_check=None,
                     batch_size: int = 50, max_members: int = 50000) -> dict:
    
    filters = filters or {"usernames_only": True}
    stats = {"scraped": 0, "scanned": 0, "failed": 0, "total": 0, "saved_db": 0}
    batch = []
    owner_id = str(owner_id)
    errors = []
    
    recent_members = []
    last_preview_update = [0.0]

    def _push_preview(user):
        try:
            entry = {
                "id": str(user.id),
                "name": (getattr(user, "first_name", "") or "")[:20],
                "username": getattr(user, "username", "") or "",
            }
            recent_members.append(entry)
            if len(recent_members) > 10: recent_members.pop(0)
            now = _time.time()
            if now - last_preview_update[0] >= 1.0:
                progress.update_members_preview(task_id, recent_members[-10:])
                last_preview_update[0] = now
        except: pass

    # ═══ دالة الحفظ في الداتابيس ═══
    async def flush():
        nonlocal batch
        if not batch: return 0
        n = members_q.bulk_insert(batch, owner_id)
        batch = []
        stats["saved_db"] += n
        log.info(f"Scrape {task_id}: Saved {n} members to vault")
        return n

    # ═══ محاولة جلب اسم الجروب ═══
    try:
        chat = await asyncio.wait_for(client.get_chat(target_chat), timeout=15)
        stats["total"] = getattr(chat, "members_count", 0) or 0
        progress.update(task_id, reason=f"بدأ السحب (الجروب {stats['total']} عضو)")
    except Exception:
        progress.update(task_id, reason="بدأ السحب...")

    # ═══ السحب من التاريخ (History) ═══
    try:
        async for msg in client.get_chat_history(target_chat):
            if cancel_check and cancel_check():
                await flush() # حفظ اللي اتسحب قبل الإيقاف
                progress.finish(task_id, "cancelled")
                return stats
                
            if not getattr(msg, "from_user", None):
                continue
                
            stats["scanned"] += 1
            progress.increment(task_id, "scanned")
            
            user = msg.from_user
            check = should_scrape(user, filters)
            if not check["ok"]:
                stats["failed"] += 1
                progress.increment(task_id, "failed")
                continue
            
            if is_blacklisted(str(user.id), owner_id):
                continue
            
            _push_preview(user)
            batch.append(make_member_tuple(user, str(target_chat)))
            stats["scraped"] += 1
            progress.increment(task_id, "scraped")
            
            # ═══ الحفظ التلقائي كل 50 عضو ═══
            if len(batch) >= batch_size:
                await flush()
                progress.update(task_id, reason=f"تم فحص {stats['scanned']} | تم حفظ {stats['saved_db']} في المخزن")
            
            if stats["scraped"] >= max_members:
                break
                
    except Exception as e:
        err_str = str(e)
        errors.append(err_str)
        log.warning(f"History scrape error: {err_str[:80]}")
        
        if "FloodWait" in err_str:
            progress.update(task_id, reason=f"⏱️ تليجرام طلب انتظار... سيتم الاستكمال.")
    
    # ═══ حفظ الباقي ═══
    await flush()
    progress.update_members_preview(task_id, recent_members[-10:])
    
    # ═══ النتيجة النهائية ═══
    if stats["scraped"] > 0:
        progress.finish(task_id, "completed")
        if stats['saved_db'] > 0:
            reason = f"✅ تم سحب وحفظ {stats['saved_db']} عضو جديد في المخزن"
        else:
            reason = f"✅ تم فحص {stats['scraped']} عضو، لكنهم موجودين في المخزن بالفعل (لا يوجد جديد)."
        if errors: reason += f" (مع بعض التحذيرات)"
        progress.update(task_id, reason=reason)
    else:
        progress.finish(task_id, "failed")
        progress.update(task_id, reason="❌ لم يتم العثور على أعضاء بيوزر.")
        
    log.info(f"Scrape {task_id}: scraped={stats['scraped']} saved_to_db={stats['saved_db']}")
    return stats
