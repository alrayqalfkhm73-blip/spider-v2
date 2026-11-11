"""Test Data Seeder"""
import random
from database.connection import get_db
from database import apply_all
from logger import get_logger

log = get_logger("seed")
db = get_db()

def seed_users(count: int = 10):
    for i in range(count):
        uid = f"test_user_{i}_{random.randint(1000, 9999)}"
        db.execute("INSERT OR IGNORE INTO users (id, points, role, joined_at) VALUES (?, ?, ?, datetime('now'))",
                   (uid, random.randint(100, 50000), random.choice(["USER", "USER", "VIP"])),
                   commit=True)
    log.info(f"Seeded {count} users")

def seed_members(owner: str, count: int = 50):
    with db.transaction():
        for i in range(count):
            uid = f"member_{i}_{random.randint(1000, 99999)}"
            db.execute("INSERT OR IGNORE INTO members (id, username, user_id, scraped_from, scraped_at, owner_user_id) VALUES (?, ?, ?, ?, datetime('now'), ?)",
                       (f"@{uid}", f"u{i}", uid, "test_group", owner))
    log.info(f"Seeded {count} members for {owner}")

def seed_all(owner: str = "8813635835"):
    apply_all()
    seed_users(10)
    seed_members(owner, 50)
    log.info("All test data seeded")

if __name__ == "__main__":
    seed_all()
    print("✅ Seeded")
