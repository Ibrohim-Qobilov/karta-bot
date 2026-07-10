"""PIN himoyasi: qulflash holati va kartalarni ko'rsatishdan oldingi tekshiruv."""
import time

import database as db
from locales import t
from states import Unlock
from .common import show_cards

# PIN kiritilgach necha soniya qayta so'ralmaydi
UNLOCK_TTL = 60  # 1 daqiqa — keyin avtomatik qulflanadi

# Brute-force himoya: necha marta xato / bloklash davomiyligi
MAX_PIN_TRIES = 5
PIN_BLOCK = 60  # soniya

# user_id -> qulf ochilishi tugaydigan vaqt (time.monotonic)
_unlocked = {}
# user_id -> [xato urinishlar soni, bloklash tugaydigan vaqt (monotonic)]
_fails = {}


def unlock(user_id):
    _unlocked[user_id] = time.monotonic() + UNLOCK_TTL


def lock(user_id):
    _unlocked.pop(user_id, None)


def is_unlocked(user_id):
    expires = _unlocked.get(user_id)
    return expires is not None and expires > time.monotonic()


def pin_block_left(user_id):
    """Bloklash tugashiga qolgan butun soniya (bloklanmagan bo'lsa 0)."""
    st = _fails.get(user_id)
    if not st:
        return 0
    left = st[1] - time.monotonic()
    return int(left) + 1 if left > 0 else 0


def _register_pin_fail(user_id):
    """Xato PIN'ni qayd etadi. Limitga yetsa bloklaydi va qolgan soniyani qaytaradi."""
    st = _fails.get(user_id) or [0, 0.0]
    st[0] += 1
    if st[0] >= MAX_PIN_TRIES:
        st[1] = time.monotonic() + PIN_BLOCK
        st[0] = 0
    _fails[user_id] = st
    return pin_block_left(user_id)


def reset_pin_fails(user_id):
    _fails.pop(user_id, None)


async def verify_with_limit(user_id, pin):
    """PIN'ni urinish cheklovi bilan tekshiradi.

    Qaytaradi: ("blocked", qolgan_soniya) | ("ok", 0) | ("wrong", 0).
    """
    left = pin_block_left(user_id)
    if left > 0:
        return "blocked", left
    if await db.verify_pin(user_id, pin):
        reset_pin_fails(user_id)
        return "ok", 0
    left = _register_pin_fail(user_id)
    if left > 0:
        return "blocked", left
    return "wrong", 0


async def show_cards_guarded(target, state, user_id):
    """PIN o'rnatilgan va hali qulf ochilmagan bo'lsa — avval PIN so'raydi."""
    if not await require_unlock(target, state, user_id, "view"):
        return
    lang = await db.get_lang(user_id)
    await show_cards(target, lang, user_id)


async def require_unlock(target, state, user_id, pending):
    """Maxfiy amal uchun PIN tekshiruvi.

    PIN yo'q yoki qulf ochiq bo'lsa — True (amalni darrov bajarish mumkin).
    Aks holda `pending` amalni eslab qolib PIN so'raydi va False qaytaradi;
    PIN to'g'ri kiritilgach `Unlock.pin` handleri o'sha amalni davom ettiradi.
    """
    if not await db.has_pin(user_id) or is_unlocked(user_id):
        return True
    lang = await db.get_lang(user_id)
    await state.update_data(pending=pending)
    await state.set_state(Unlock.pin)
    await target.answer(t(lang, "pin_enter"))
    return False
