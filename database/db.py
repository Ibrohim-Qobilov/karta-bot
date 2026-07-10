"""SQLite bilan ishlash. Karta raqami Fernet bilan shifrlab saqlanadi."""
import hashlib
import logging

import aiosqlite
from cryptography.fernet import Fernet, InvalidToken

from config import DB_PATH, ENCRYPTION_KEY

logger = logging.getLogger(__name__)
fernet = Fernet(ENCRYPTION_KEY.encode())


async def _ensure_column(db, table, column, coltype):
    """Eski bazaga yetishmayotgan ustunni qo'shadi (migratsiya)."""
    async with db.execute(f"PRAGMA table_info({table})") as cur:
        columns = [row[1] for row in await cur.fetchall()]
    if column not in columns:
        await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang    TEXT DEFAULT 'uz',
                pin     TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name    TEXT,
                number  TEXT,
                holder  TEXT
            )
        """)
        # eski bazalar uchun migratsiya
        await _ensure_column(db, "users", "pin", "TEXT")
        await db.commit()


# ---------- til ----------

async def set_lang(user_id, lang):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (user_id, lang) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang = ?",
            (user_id, lang, lang),
        )
        await db.commit()


async def get_lang(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else "uz"


# ---------- PIN-kod ----------

def _hash_pin(user_id, pin):
    """PIN ochiq saqlanmaydi — user_id bilan tuzlangan sha256 hash."""
    return hashlib.sha256(f"{user_id}:{pin}".encode()).hexdigest()


async def set_pin(user_id, pin):
    h = _hash_pin(user_id, pin)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (user_id, pin) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET pin = ?",
            (user_id, h, h),
        )
        await db.commit()


async def clear_pin(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET pin = NULL WHERE user_id = ?", (user_id,))
        await db.commit()


async def has_pin(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row and row[0])


async def verify_pin(user_id, pin):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
    return bool(row and row[0]) and row[0] == _hash_pin(user_id, pin)


# ---------- kartalar ----------

async def add_card(user_id, name, number, holder):
    enc = fernet.encrypt(number.encode()).decode()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO cards (user_id, name, number, holder) VALUES (?, ?, ?, ?)",
            (user_id, name, enc, holder),
        )
        await db.commit()


async def get_cards(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, name, number, holder FROM cards WHERE user_id = ?", (user_id,)
        ) as cur:
            rows = await cur.fetchall()
    cards = []
    for cid, name, enc, holder in rows:
        try:
            number = fernet.decrypt(enc.encode()).decode()
        except InvalidToken:
            logger.warning("Karta #%s deshifrlab bo'lmadi (user %s) — o'tkazib yuborildi", cid, user_id)
            continue
        cards.append({"id": cid, "name": name, "number": number, "holder": holder})
    return cards


async def get_card(user_id, card_id):
    for c in await get_cards(user_id):
        if c["id"] == card_id:
            return c
    return None


async def name_exists(user_id, name, exclude_id=None):
    for c in await get_cards(user_id):
        if c["name"].lower() == name.lower() and c["id"] != exclude_id:
            return True
    return False


async def find_by_number(user_id, number, exclude_id=None):
    for c in await get_cards(user_id):
        if c["number"] == number and c["id"] != exclude_id:
            return c
    return None


async def update_name(user_id, card_id, name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cards SET name = ? WHERE id = ? AND user_id = ?", (name, card_id, user_id)
        )
        await db.commit()


async def update_holder(user_id, card_id, holder):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cards SET holder = ? WHERE id = ? AND user_id = ?", (holder, card_id, user_id)
        )
        await db.commit()


async def update_number(user_id, card_id, number):
    enc = fernet.encrypt(number.encode()).decode()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cards SET number = ? WHERE id = ? AND user_id = ?", (enc, card_id, user_id)
        )
        await db.commit()


async def delete_card(user_id, card_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cards WHERE id = ? AND user_id = ?", (card_id, user_id))
        await db.commit()
