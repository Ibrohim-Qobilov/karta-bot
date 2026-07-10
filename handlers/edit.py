"""Kartani tahrirlash va o'chirish (tasdiqlash bilan)."""
from aiogram import Router, F # pyright: ignore[reportMissingImports]
from aiogram.fsm.context import FSMContext # pyright: ignore[reportMissingImports]
from aiogram.types import CallbackQuery, Message # pyright: ignore[reportMissingImports]

import database as db
from keyboards import main_menu, edit_menu_kb, delete_confirm_kb, luhn_kb
from locales import t
from states import EditCard
from utils.text import MENU_EMOJIS, mask, only_digits, luhn_valid
from .common import show_cards, edit_to_cards
from .security import require_unlock

router = Router()


# ---------- o'chirish ----------

async def ask_delete(target, lang, user_id, card_id):
    """O'chirishni tasdiqlash xabarini yangi xabar sifatida ko'rsatadi (PIN'dan keyin)."""
    c = await db.get_card(user_id, card_id)
    if not c:
        return
    text = f"{t(lang, 'del_confirm_title')}\n\n{mask(c['number'])}\n\n{t(lang, 'del_confirm_note')}"
    await target.answer(text, reply_markup=delete_confirm_kb(lang, card_id))


@router.callback_query(F.data.startswith("delask:"))
async def cb_delask(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_lang(user_id)
    card_id = int(call.data.split(":")[1])
    # O'chirishdan oldin PIN (o'rnatilgan bo'lsa).
    if not await require_unlock(call.message, state, user_id, f"delete:{card_id}"):
        await call.answer()
        return
    c = await db.get_card(user_id, card_id)
    if not c:
        await call.answer()
        return
    text = f"{t(lang, 'del_confirm_title')}\n\n{mask(c['number'])}\n\n{t(lang, 'del_confirm_note')}"
    await call.message.edit_text(text, reply_markup=delete_confirm_kb(lang, card_id))
    await call.answer()


@router.callback_query(F.data.startswith("delyes:"))
async def cb_delyes(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    card_id = int(call.data.split(":")[1])
    await db.delete_card(call.from_user.id, card_id)
    # o'chirilgach karuselni yangilaymiz (karta qolmasa "no_cards")
    await edit_to_cards(call.message, lang, call.from_user.id, index=0)
    await call.answer(t(lang, "deleted"))


@router.callback_query(F.data.startswith("delno:"))
async def cb_delno(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    card_id = int(call.data.split(":")[1])
    # o'chirishdan/tahrirlashdan bekor qilib, o'sha kartaga qaytamiz
    await edit_to_cards(call.message, lang, call.from_user.id, focus_id=card_id)
    await call.answer()


# ---------- tahrirlash ----------

@router.callback_query(F.data.startswith("edit:"))
async def cb_edit(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    card_id = int(call.data.split(":")[1])
    await call.message.edit_text(t(lang, "edit_menu_title"), reply_markup=edit_menu_kb(lang, card_id))
    await call.answer()


@router.callback_query(F.data.startswith("efld:"))
async def cb_edit_field(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    _, field, card_id = call.data.split(":")
    await state.update_data(edit_id=int(card_id))
    if field == "name":
        await state.set_state(EditCard.name)
        await call.message.answer(t(lang, "edit_name_prompt"))
    elif field == "holder":
        await state.set_state(EditCard.holder)
        await call.message.answer(t(lang, "edit_holder_prompt"))
    else:
        await state.set_state(EditCard.number)
        await call.message.answer(t(lang, "edit_number_prompt"))
    await call.answer()


@router.message(EditCard.name)
async def edit_name(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    name = (message.text or "").strip()
    if name.startswith(MENU_EMOJIS):
        return
    data = await state.get_data()
    cid = data["edit_id"]
    if await db.name_exists(message.from_user.id, name, exclude_id=cid):
        await message.answer(t(lang, "name_exists"))
        return
    await db.update_name(message.from_user.id, cid, name)
    await state.clear()
    await message.answer(t(lang, "edit_saved"), reply_markup=main_menu(lang))
    await show_cards(message, lang, message.from_user.id, focus_id=cid)


@router.message(EditCard.holder)
async def edit_holder(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    holder = (message.text or "").strip()
    if holder == "-":
        holder = ""
    data = await state.get_data()
    cid = data["edit_id"]
    await db.update_holder(message.from_user.id, cid, holder)
    await state.clear()
    await message.answer(t(lang, "edit_saved"), reply_markup=main_menu(lang))
    await show_cards(message, lang, message.from_user.id, focus_id=cid)


@router.message(EditCard.number)
async def edit_number(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    digits = only_digits(message.text)
    if len(digits) != 16:
        await message.answer(t(lang, "bad_number"))
        return
    data = await state.get_data()
    cid = data["edit_id"]
    existing = await db.find_by_number(message.from_user.id, digits, exclude_id=cid)
    if existing:
        holder = existing["holder"] or "-"
        text = (
            f"{t(lang, 'num_exists_title')}\n\n{t(lang, 'num_exists_body')}\n\n"
            f"💳 {existing['name']}\n{holder}\n{mask(existing['number'])}\n\n"
            f"{t(lang, 'num_exists_note')}"
        )
        await message.answer(text)
        return
    if not luhn_valid(digits):
        # Chop xatosi ehtimoli — bloklamaymiz, «baribir saqlash» taklif qilamiz.
        await state.update_data(pending_number=digits)
        await message.answer(t(lang, "luhn_warn"), reply_markup=luhn_kb(lang, edit=True))
        return
    await _commit_number(message, state, lang, message.from_user.id, cid, digits)


async def _commit_number(target, state, lang, user_id, cid, digits):
    await db.update_number(user_id, cid, digits)
    await state.clear()
    await target.answer(t(lang, "edit_saved"), reply_markup=main_menu(lang))
    await show_cards(target, lang, user_id, focus_id=cid)


@router.callback_query(F.data == "eluhn_ok")
async def cb_edit_luhn_ok(call: CallbackQuery, state: FSMContext):
    """Tahrirlashda Luhn ogohlantirishidan keyin «baribir saqlash»."""
    lang = await db.get_lang(call.from_user.id)
    data = await state.get_data()
    digits = data.get("pending_number")
    cid = data.get("edit_id")
    if not digits or cid is None:
        await call.answer()
        return
    await _commit_number(call.message, state, lang, call.from_user.id, cid, digits)
    await call.answer()


@router.callback_query(F.data == "edit_cancel")
async def cb_edit_cancel(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await state.clear()
    await call.message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))
    await call.answer()
