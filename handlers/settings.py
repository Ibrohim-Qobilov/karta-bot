"""Sozlamalar menyusi: til va PIN-kod."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

import database as db
from keyboards import lang_kb, main_menu, pin_manage_kb
from locales import t
from states import SetPin, ManagePin, Unlock
from utils.text import MENU_EMOJIS
from .common import show_cards
from .security import unlock, lock, verify_with_limit

router = Router()

# To'liq maxfiylik siyosati (Telegraph).
PRIVACY_URL = "https://telegra.ph/Karta-Bot--Maxfiylik-siyosati-07-11"


def _security_kb(lang):
    """Siyosat matni ostidagi «To'liq o'qish» (Telegraph) tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "security_full_btn"), url=PRIVACY_URL),
    ]])


def _valid_pin(text):
    text = (text or "").strip()
    return text.isdigit() and len(text) == 4


# ---------- sozlamalar callbacklari ----------

@router.callback_query(F.data == "set:lang")
async def open_lang(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t(lang, "choose_lang"), reply_markup=lang_kb())
    await call.answer()


@router.callback_query(F.data == "set:security")
async def open_security(call: CallbackQuery):
    """Xavfsizlik siyosati matnini ko'rsatadi."""
    lang = await db.get_lang(call.from_user.id)
    await call.message.answer(t(lang, "security_policy"), reply_markup=_security_kb(lang))
    await call.answer()


@router.message(Command("security", "privacy"))
async def cmd_security(message: Message):
    """/security yoki /privacy — xavfsizlik siyosatini ko'rsatadi."""
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "security_policy"), reply_markup=_security_kb(lang))


@router.callback_query(F.data == "set:pin")
async def open_pin(call: CallbackQuery, state: FSMContext):
    """PIN yo'q → o'rnatish oqimi. PIN bor → joriy PIN'ni so'rab, boshqaruv menyusini ochamiz."""
    lang = await db.get_lang(call.from_user.id)
    if await db.has_pin(call.from_user.id):
        await state.set_state(ManagePin.verify)
        await call.message.answer(t(lang, "pin_enter"))
    else:
        await state.set_state(SetPin.new)
        await call.message.answer(t(lang, "pin_set_prompt"))
    await call.answer()


# ---------- PIN boshqaruvi (joriy PIN tasdiqlangach) ----------

@router.message(ManagePin.verify)
async def pin_manage_verify(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    text = (message.text or "").strip()
    if text.startswith(MENU_EMOJIS):
        await state.clear()
        return
    status, secs = await verify_with_limit(message.from_user.id, text)
    if status == "blocked":
        await message.answer(t(lang, "pin_blocked").format(sec=secs))
        return
    if status == "wrong":
        await message.answer(t(lang, "pin_wrong"))
        return
    await state.clear()
    await message.answer(t(lang, "pin_manage_title"), reply_markup=pin_manage_kb(lang))


@router.callback_query(F.data == "pin:change")
async def pin_change(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await state.set_state(SetPin.new)
    await call.message.answer(t(lang, "pin_set_prompt"))
    await call.answer()


@router.callback_query(F.data == "pin:remove")
async def pin_remove_cb(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await db.clear_pin(call.from_user.id)
    lock(call.from_user.id)
    await state.clear()
    await call.message.answer(t(lang, "pin_removed"), reply_markup=main_menu(lang))
    await call.answer()


# ---------- PIN o'rnatish ----------

@router.message(SetPin.new)
async def pin_new(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    text = (message.text or "").strip()
    if text.startswith(MENU_EMOJIS):
        await state.clear()
        return
    if not _valid_pin(text):
        await message.answer(t(lang, "pin_bad"))
        return
    await state.update_data(pin=text)
    await state.set_state(SetPin.confirm)
    await message.answer(t(lang, "pin_confirm_prompt"))


@router.message(SetPin.confirm)
async def pin_confirm(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    text = (message.text or "").strip()
    if text.startswith(MENU_EMOJIS):
        await state.clear()
        return
    data = await state.get_data()
    if text != data.get("pin"):
        await state.set_state(SetPin.new)
        await message.answer(t(lang, "pin_mismatch"))
        return
    await db.set_pin(message.from_user.id, text)
    unlock(message.from_user.id)
    await state.clear()
    await message.answer(t(lang, "pin_saved"), reply_markup=main_menu(lang))


# ---------- qulfni ochish (kartalarni ko'rish uchun) ----------

@router.message(Unlock.pin)
async def unlock_pin(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    text = (message.text or "").strip()
    if text.startswith(MENU_EMOJIS):
        await state.clear()
        return
    user_id = message.from_user.id
    status, secs = await verify_with_limit(user_id, text)
    if status == "blocked":
        await message.answer(t(lang, "pin_blocked").format(sec=secs))
        return
    if status == "wrong":
        await message.answer(t(lang, "pin_wrong"))
        return
    unlock(user_id)
    data = await state.get_data()
    pending = data.get("pending")
    await state.clear()
    # PIN kutilgan maxfiy amalni davom ettiramiz.
    if pending == "export":
        from .backup import send_export
        await send_export(message, lang, user_id)
    elif pending == "import":
        from .backup import start_import
        await start_import(message, state, lang)
    elif pending and pending.startswith("delete:"):
        from .edit import ask_delete
        await ask_delete(message, lang, user_id, int(pending.split(":")[1]))
    else:  # "view" yoki noma'lum — kartalarni ko'rsatamiz
        await show_cards(message, lang, user_id)
