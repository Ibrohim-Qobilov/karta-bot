"""Karta qo'shish (FSM) va kartalarni ko'rish."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import main_menu, flow_kb, noname_kb, luhn_kb, inline_try_kb
from locales import t
from states import AddCard
from utils.text import MENU_EMOJIS, mask, only_digits, luhn_valid
from .common import show_cards, edit_to_cards
from .security import show_cards_guarded

router = Router()


# ---------- qo'shishni boshlash ----------

async def start_add(target, state, lang):
    await state.set_state(AddCard.name)
    await target.answer(t(lang, "add_name"))


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    await start_add(message, state, lang)


# ---------- 1/3: nom ----------

@router.message(AddCard.name)
async def step_name(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    name = (message.text or "").strip()
    if name.startswith(MENU_EMOJIS):
        return
    if await db.name_exists(message.from_user.id, name):
        await message.answer(t(lang, "name_exists"))
        return
    await state.update_data(name=name)
    await state.set_state(AddCard.number)
    await message.answer(t(lang, "add_number"), reply_markup=flow_kb(lang))


# ---------- 2/3: raqam ----------

@router.message(AddCard.number)
async def step_number(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    digits = only_digits(message.text)
    if len(digits) != 16:
        await message.answer(t(lang, "bad_number"), reply_markup=flow_kb(lang))
        return
    existing = await db.find_by_number(message.from_user.id, digits)
    if existing:
        holder = existing["holder"] or "-"
        text = (
            f"{t(lang, 'num_exists_title')}\n\n{t(lang, 'num_exists_body')}\n\n"
            f"💳 {existing['name']}\n{holder}\n{mask(existing['number'])}\n\n"
            f"{t(lang, 'num_exists_note')}"
        )
        await message.answer(text, reply_markup=flow_kb(lang))
        return
    if not luhn_valid(digits):
        # Chop xatosi ehtimoli — bloklamaymiz, «baribir saqlash» taklif qilamiz.
        await state.update_data(pending_number=digits)
        await message.answer(t(lang, "luhn_warn"), reply_markup=luhn_kb(lang))
        return
    await _go_holder(message, state, lang, digits, message.from_user)


async def _go_holder(target, state, lang, digits, user):
    await state.update_data(number=digits)
    await state.set_state(AddCard.holder)
    # Misol sifatida foydalanuvchining o'z ismi-familiyasini ko'rsatamiz.
    name = " ".join(filter(None, [user.first_name, user.last_name])).strip() or "Ibrohim Qobilov"
    await target.answer(t(lang, "add_holder").format(name=name), reply_markup=noname_kb(lang))


@router.callback_query(F.data == "luhn_ok")
async def cb_luhn_ok(call: CallbackQuery, state: FSMContext):
    """Luhn ogohlantirishidan keyin «baribir saqlash» — egasi bosqichiga o'tamiz."""
    lang = await db.get_lang(call.from_user.id)
    data = await state.get_data()
    digits = data.get("pending_number")
    if not digits:
        await call.answer()
        return
    await _go_holder(call.message, state, lang, digits, call.from_user)
    await call.answer()


# ---------- 3/3: egasi ----------

@router.message(AddCard.holder)
async def step_holder(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    await finish_add(message, state, lang, (message.text or "").strip(), message.from_user.id)


async def finish_add(target, state, lang, holder, user_id):
    data = await state.get_data()
    await db.add_card(user_id, data["name"], data["number"], holder)
    await state.clear()
    await target.answer(t(lang, "card_added"), reply_markup=main_menu(lang))
    await show_cards(target, lang, user_id, index=-1)  # eng yangi karta
    # Birinchi karta qo'shilganda — inline'ni sinab ko'rishga qo'llanma.
    cards = await db.get_cards(user_id)
    if len(cards) == 1:
        await target.answer(t(lang, "inline_tip"), reply_markup=inline_try_kb(lang))


@router.callback_query(F.data == "save_noname")
async def cb_noname(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await finish_add(call.message, state, lang, "", call.from_user.id)
    await call.answer()


@router.callback_query(F.data == "add_back")
async def cb_back(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await state.set_state(AddCard.name)
    await call.message.answer(t(lang, "add_name"))
    await call.answer()


@router.callback_query(F.data == "add_cancel")
async def cb_cancel(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await state.clear()
    await call.message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))
    await call.answer()


# ---------- kartalarni ko'rish ----------

@router.message(Command("karta", "card"))
async def cmd_karta(message: Message, state: FSMContext):
    # Guruh/kanal chatlarida: PINsiz, faqat ko'rish rejimida ko'rsatamiz
    # (PIN guruhda so'ralsa hamma ko'rib qoladi + FSM holati guruhga tegishli bo'lardi).
    if message.chat.type != "private":
        lang = await db.get_lang(message.from_user.id)
        await show_cards(message, lang, message.from_user.id, readonly=True)
        return
    await show_cards_guarded(message, state, message.from_user.id)


# ---------- karuselni varaqlash ----------

@router.callback_query(F.data.startswith("nav:"))
async def cb_nav(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    parts = call.data.split(":")
    index = int(parts[1])
    owner_id = int(parts[2]) if len(parts) > 2 else None
    # Guruhdagi karusel (nav:i:owner) — faqat karta egasi varaqlay oladi.
    if owner_id is not None and owner_id != call.from_user.id:
        await call.answer(t(lang, "not_your_card"), show_alert=True)
        return
    readonly = owner_id is not None
    await edit_to_cards(call.message, lang, call.from_user.id, index=index, readonly=readonly)
    await call.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()
