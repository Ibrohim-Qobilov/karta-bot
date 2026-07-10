"""Zaxira nusxa: kartalarni JSON fayl sifatida yuklab olish (export) va tiklash (import).

Fayl foydalanuvchining o'z chatiga yuboriladi va uni istalgan botga tiklash mumkin.
Diqqat: fayl ichida karta raqamlari ochiq — foydalanuvchi buni bilishi kerak.
"""
import json
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

import database as db
from keyboards import main_menu
from locales import t
from states import Backup
from utils.text import only_digits
from .security import require_unlock

router = Router()
logger = logging.getLogger(__name__)

MAX_IMPORT_BYTES = 1_000_000  # 1 MB — zaxira fayli uchun yetarli
MAX_CARDS = 500


# ---------- export ----------

async def send_export(target, lang, user_id):
    """Kartalarni JSON fayl sifatida yuboradi (PIN allaqachon tekshirilgan)."""
    cards = await db.get_cards(user_id)
    if not cards:
        await target.answer(t(lang, "export_empty"))
        return
    payload = {
        "version": 1,
        "cards": [
            {"name": c["name"], "number": c["number"], "holder": c["holder"] or ""}
            for c in cards
        ],
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    doc = BufferedInputFile(data, filename="karta_backup.json")
    await target.answer_document(doc, caption=t(lang, "export_caption"))


@router.callback_query(F.data == "set:export")
async def cb_export(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_lang(user_id)
    if not await require_unlock(call.message, state, user_id, "export"):
        await call.answer()
        return
    await send_export(call.message, lang, user_id)
    await call.answer()


# ---------- import ----------

async def start_import(target, state, lang):
    """Import oqimini boshlaydi (PIN allaqachon tekshirilgan)."""
    await state.set_state(Backup.file)
    await target.answer(t(lang, "import_prompt"))


@router.callback_query(F.data == "set:import")
async def cb_import(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_lang(user_id)
    if not await require_unlock(call.message, state, user_id, "import"):
        await call.answer()
        return
    await start_import(call.message, state, lang)
    await call.answer()


async def _unique_name(user_id, name):
    """Import paytida nom takrorlanmasligi uchun oxiriga son qo'shadi."""
    base = name or "Karta"
    name = base
    i = 2
    while await db.name_exists(user_id, name):
        name = f"{base} ({i})"
        i += 1
    return name


@router.message(Backup.file, F.document)
async def import_file(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    user_id = message.from_user.id

    if (message.document.file_size or 0) > MAX_IMPORT_BYTES:
        await message.answer(t(lang, "import_bad_file"))
        return

    try:
        buf = await message.bot.download(message.document)
        payload = json.loads(buf.read().decode("utf-8"))
        entries = payload["cards"] if isinstance(payload, dict) else payload
        assert isinstance(entries, list)
    except (json.JSONDecodeError, UnicodeDecodeError, KeyError, AssertionError, TypeError):
        await state.clear()
        await message.answer(t(lang, "import_bad_file"), reply_markup=main_menu(lang))
        return

    added = skipped = 0
    for entry in entries[:MAX_CARDS]:
        if not isinstance(entry, dict):
            skipped += 1
            continue
        number = only_digits(entry.get("number"))
        if len(number) != 16:
            skipped += 1
            continue
        if await db.find_by_number(user_id, number):  # dublikat raqam
            skipped += 1
            continue
        name = await _unique_name(user_id, str(entry.get("name") or "").strip())
        holder = str(entry.get("holder") or "").strip()
        await db.add_card(user_id, name, number, holder)
        added += 1

    await state.clear()
    await message.answer(
        t(lang, "import_done").format(added=added, skipped=skipped),
        reply_markup=main_menu(lang),
    )


@router.message(Backup.file)
async def import_not_a_file(message: Message):
    """Import kutilayotganda hujjat o'rniga matn kelsa — eslatib qo'yamiz."""
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "import_prompt"))
