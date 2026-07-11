"""Botni ishga tushirish."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ErrorEvent

import database as db
import handlers
from config import BOT_TOKEN
from locales import t

logger = logging.getLogger(__name__)


async def on_error(event: ErrorEvent):
    """Har qanday handler'dagi ushlanmagan xatoni jurnalga yozadi va
    foydalanuvchiga xushmuomala xabar qaytaradi (bot yiqilmaydi)."""
    logger.exception("Update ishlovida xatolik: %s", event.exception)
    upd = event.update
    user = chat_msg = None
    if upd.message:
        user, chat_msg = upd.message.from_user, upd.message
    elif upd.callback_query:
        user, chat_msg = upd.callback_query.from_user, upd.callback_query.message
        try:
            await upd.callback_query.answer()
        except Exception:  # noqa: BLE001 — bildirishnoma muhim emas
            pass
    if user is not None and chat_msg is not None:
        try:
            lang = await db.get_lang(user.id)
            await chat_msg.answer(t(lang, "error"))
        except Exception:  # noqa: BLE001 — foydalanuvchiga yozib bo'lmasa, jim o'tamiz
            pass
    return True


async def set_commands(bot):
    await bot.set_my_commands([
        BotCommand(command="karta", description="Kartalarim / My cards"),
        BotCommand(command="card", description="Kartalarim / My cards"),
        BotCommand(command="add", description="Karta qo'shish / Add card"),
        BotCommand(command="start", description="Boshlash / Start"),
        BotCommand(command="security", description="Xavfsizlik / Security"),
    ])


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    await db.init_db()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(*handlers.routers)
    dp.errors.register(on_error)

    await set_commands(bot)

    logger.info("Bot ishga tushdi ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
