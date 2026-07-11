"""/start va til tanlash."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import main_menu, lang_kb
from locales import t

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Birinchi kirishda til so'raladi, keyin saqlangan tilda asosiy menyu."""
    await state.clear()
    if await db.user_exists(message.from_user.id):
        lang = await db.get_lang(message.from_user.id)
        await message.answer(t(lang, "start"), reply_markup=main_menu(lang))
    else:
        await message.answer(t("uz", "choose_lang"), reply_markup=lang_kb())


@router.callback_query(F.data.startswith("lang:"))
async def choose_lang(call: CallbackQuery):
    lang = call.data.split(":")[1]
    await db.set_lang(call.from_user.id, lang)
    await call.message.edit_text(t(lang, "lang_saved"))
    await call.message.answer(t(lang, "start"), reply_markup=main_menu(lang))
    await call.answer()
