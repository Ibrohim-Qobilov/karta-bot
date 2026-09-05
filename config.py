"""Sozlamalar — barcha maxfiy qiymatlar `.env` faylidan o'qiladi."""
import os

from dotenv import load_dotenv

load_dotenv()


def _required(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"«{name}» muhit o'zgaruvchisi topilmadi. "
            f".env faylini to'ldiring (.env.example ga qarang)."
        )
    return value


BOT_TOKEN = _required("BOT_TOKEN")
ENCRYPTION_KEY = _required("ENCRYPTION_KEY")
DB_PATH = os.getenv("DB_PATH", "cards.db")
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")
