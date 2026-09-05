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


import os
from aiohttp import web

async def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Tez Karta Bot is live! 💳"))
    app.router.add_get("/health", lambda r: web.Response(text="OK"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server listening on port %d", port)
    return runner


import aiohttp

async def keep_alive_loop():
    await asyncio.sleep(60)
    urls = [
        "https://karta-bot-nndu.onrender.com/health",
        "https://bozorlik-bot.onrender.com/health",
        "https://aloqa-bot-x0ho.onrender.com/health",
    ]
    async with aiohttp.ClientSession() as session:
        while True:
            for u in urls:
                try:
                    async with session.get(u, timeout=aiohttp.ClientTimeout(total=10)):
                        pass
                except Exception:
                    pass
            await asyncio.sleep(8 * 60)


async def set_commands(bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="▶️ Boshlash"),
        BotCommand(command="karta", description="💳 Kartalarim"),
        BotCommand(command="add", description="➕ Karta qo'shish"),
        BotCommand(command="security", description="🔐 Xavfsizlik"),
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

    web_runner = None
    if os.environ.get("PORT"):
        web_runner = await start_health_server()

    keep_alive_task = asyncio.create_task(keep_alive_loop())

    logger.info("Bot ishga tushdi ✅")
    try:
        await dp.start_polling(bot)
    finally:
        keep_alive_task.cancel()
        if web_runner:
            await web_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
