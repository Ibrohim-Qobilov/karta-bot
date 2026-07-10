"""Kartalar karuseli — bitta xabar, ◀️ N/M ▶️ bilan varaqlanadi."""
import database as db
from keyboards import card_view_kb
from locales import t
from utils.text import card_text


def index_of(cards, card_id):
    for i, c in enumerate(cards):
        if c["id"] == card_id:
            return i
    return 0


async def _load_view(user_id, lang, index=0, focus_id=None, readonly=False):
    """(matn, klaviatura) qaytaradi. Karta bo'lmasa (None, None)."""
    cards = await db.get_cards(user_id)
    if not cards:
        return None, None
    if focus_id is not None:
        index = index_of(cards, focus_id)
    index %= len(cards)  # aylanma
    c = cards[index]
    kb = card_view_kb(lang, c["id"], index, len(cards), readonly=readonly, owner_id=user_id, number=c["number"])
    return card_text(c), kb


async def show_cards(target, lang, user_id, index=0, focus_id=None, readonly=False):
    """Yangi xabar sifatida karuselni ko'rsatadi."""
    text, kb = await _load_view(user_id, lang, index, focus_id, readonly)
    if text is None:
        await target.answer(t(lang, "no_cards"))
        return
    await target.answer(text, reply_markup=kb, parse_mode="HTML")


async def edit_to_cards(message, lang, user_id, index=0, focus_id=None, readonly=False):
    """Mavjud xabarni karuselga aylantiradi (varaqlash / orqaga qaytish)."""
    text, kb = await _load_view(user_id, lang, index, focus_id, readonly)
    if text is None:
        await message.edit_text(t(lang, "no_cards"))
        return
    await message.edit_text(text, reply_markup=kb, parse_mode="HTML")
