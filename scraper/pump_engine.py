"""Pump Engine — Fixed Async Generator Error"""
import asyncio
import random
import time as _time
from database.queries import members as members_q, sessions as sess_q
from database.connection import get_db
from scraper import progress
from logger import get_logger

log = get_logger("scraper.pump")
db = get_db()

async def run_pump(clients: list, target_chat, owner_id: str, task_id: str,
                   mode: str = "safe", cancel_check=None,
                   max_pumps: int = 100) -> dict:
    
    delays = {"safe": (60, 90), "fast": (30, 60), "turbo": (10, 20), "عادي": (30, 60), "آمن": (60, 90), "سريع": (30, 60), "توربو": (10, 20)}
    delay_min, delay_max = delays.get(mode, (30, 60))
    
    members = members_q.get_paginated(str(owner_id), limit=max_pumps)
    if not members:
        progress.finish(task_id, "failed")
        progress.update(task_id, reason="المخزن فاضي - اسحب أعضاء الأول")
        return {"success": 0, "failed": 0, "reason": "vault_empty"}
        
    stats = {"success": 0, "failed": 0}
    recent_members = []
    last_preview = [0.0]
    last_error_msg = "جاري المحاولة..."

    try:
        target_id = int(target_chat)
    except ValueError:
        target_id = target_chat

    def _push_preview(member_dict):
        try:
            entry = {"id": str(member_dict.get("id", "")), "name": (member_dict.get("username") or member_dict.get("id", ""))[:20], "username": member_dict.get("username") or ""}
            recent_members.append(entry)
            if len(recent_members) > 10: recent_members.pop(0)
            now = _time.time()
            if now - last_preview[0] >= 1.0:
                progress.update_members_preview(task_id, recent_members[-10:])
                last_preview[0] = now
        except: pass

    available_clients = list(clients)
    
    for i, member in enumerate(members):
        if cancel_check and cancel_check():
            progress.finish(task_id, "cancelled")
            return stats
            
        mid = member.get("id")
        if not mid:
            stats["failed"] += 1
            continue
            
        _push_preview(member)
        try:
            target = mid if str(mid).startswith("@") else int(mid)
        except:
            stats["failed"] += 1
            last_error_msg = "ID غير صالح"
            continue

        success = False
        
        if not available_clients:
            progress.update(task_id, reason="⏱️ كل الجلسات في انتظار (FloodWait)...")
            await asyncio.sleep(30)
            available_clients = list(clients)
            if not available_clients: break
            
        current_client = available_clients.pop(0)
        sess_name = current_client.name
        
        try:
            # ═══ إصلاح الخطأ: استخدام async for بدل await ═══
            try:
                async for _ in current_client.get_dialogs(limit=50):
                    pass
            except Exception:
                pass
            
            await asyncio.wait_for(current_client.add_chat_members(target_id, target), timeout=30)
            success = True
            available_clients.append(current_client)
            try: sess_q.increment_pump(sess_name)
            except: pass
            
        except asyncio.TimeoutError:
            last_error_msg = "انتهت مهلة الاتصال (Timeout)"
            available_clients.append(current_client)
        except Exception as e:
            err = str(e).upper()
            last_error_msg = err[:50]
            
            if "USER_ALREADY_PARTICIPANT" in err or "ALREADY_PARTICIPANT" in err:
                success = True
                available_clients.append(current_client)
            elif "PEER_FLOOD" in err or "FLOOD_WAIT" in err:
                wait_time = 60
                try:
                    import re
                    m = re.search(r'(\d+)', err)
                    if m: wait_time = min(int(m.group(1)), 900)
                except: pass
                async def _restore(c, t):
                    await asyncio.sleep(t)
                    available_clients.append(c)
                asyncio.create_task(_restore(current_client, wait_time))
            else:
                available_clients.append(current_client)

        if success:
            stats["success"] += 1
            progress.increment(task_id, "scraped")
            try: members_q.delete_member(mid, str(owner_id))
            except: pass
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        else:
            stats["failed"] += 1
            progress.increment(task_id, "failed")
            await asyncio.sleep(random.uniform(2, 5))
            
        if not success:
            progress.update(task_id, reason=f"❌ فشل: {last_error_msg} | تقدم {i+1}/{len(members)}")
        else:
            if (i + 1) % 5 == 0:
                progress.update(task_id, reason=f"تقدم {i+1}/{len(members)} - ✅{stats['success']} ❌{stats['failed']}")
            
    progress.update_members_preview(task_id, recent_members[-10:])
    progress.finish(task_id, "completed")
    
    if stats["success"] > 0:
        progress.update(task_id, reason=f"✅ انتهى: نجح {stats['success']} | فشل {stats['failed']}")
    else:
        progress.update(task_id, reason=f"❌ فشل الكل. آخر خطأ: {last_error_msg}")
        
    return stats
