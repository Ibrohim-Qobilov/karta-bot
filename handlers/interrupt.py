"""Menyu tugmasi oqim o'rtasida bosilsa — oqimni bekor qilib, o'sha menyuга o'tadi.

Bu router eng birinchi ulanadi, shuning uchun FSM holati ichida ham
(karta raqami, PIN va h.k. kutilayotganda) menyu tugmalari ishlab ketadi va
tugma matni "noto'g'ri kiritma" sifatida qabul qilinmaydi.
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import database as db
from keyboards import settings_kb
from locales import t
from .cards import start_add
from .security import show_cards_guarded, is_unlocked

router = Router()


@router.message(F.text.startswith("➕"))
async def i_add(message: Message, state: FSMContext):
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    await start_add(message, state, lang)


@router.message(F.text.startswith("📋"))
async def i_cards(message: Message, state: FSMContext):
    await state.clear()
    await show_cards_guarded(message, state, message.from_user.id)


@router.message(F.text.startswith("⚙️"))
async def i_settings(message: Message, state: FSMContext):
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    has = await db.has_pin(message.from_user.id)
    unlocked = is_unlocked(message.from_user.id)
    await message.answer(t(lang, "settings_menu"), reply_markup=settings_kb(lang, has, unlocked))
