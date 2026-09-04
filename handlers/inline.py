"""Inline rejim — istalgan chatda `@bot` orqali kartani chaqirib yuborish.

Foydalanuvchi istalgan chatda `@tezkartabot` deb yozsa, o'z kartalari ro'yxati
chiqadi; bittasini bossa — o'sha chatga karta ma'lumoti yuboriladi.
`@tezkartabot uzum` — nom bo'yicha filtrlaydi.

Diqqat: inline'da Telegram PIN so'ramaydi — bu himoya faqat bot chatida ishlaydi.
"""
from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultsButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CopyTextButton,
)

import database as db
from locales import t
from utils.text import mask, card_brand, only_digits

router = Router()


@router.inline_query()
async def inline_cards(query: InlineQuery):
    user_id = query.from_user.id
    lang = await db.get_lang(user_id)
    needle = (query.query or "").strip().lower()

    cards = await db.get_cards(user_id)
    if needle:
        cards = [c for c in cards if needle in c["name"].lower()]

    results = []
    for c in cards[:50]:
        brand = card_brand(c["number"])
        # Karta raqami toza spoiler ichida (code tegisiz, chunki code tegi bo'lsa Telegram spoilerni xiralashtirmaydi)
        spoilered_number = f"<tg-spoiler>{mask(c['number'])}</tg-spoiler>"
        text = f"{brand}\n{spoilered_number}" if brand else spoilered_number
        results.append(InlineQueryResultArticle(
            id=str(c["id"]),
            title=c["name"],
            description=(brand + " · " if brand else "") + "•••• " + c["number"][-4:],
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML",
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=t(lang, "copy_btn"),
                    copy_text=CopyTextButton(text=only_digits(c["number"])),
                )
            ]]),
        ))

    # Karta bo'lmasa — botni ochib qo'shishga taklif qiluvchi tugma.
    button = None
    if not results:
        button = InlineQueryResultsButton(
            text=t(lang, "inline_no_cards"),
            start_parameter="add",
        )

    await query.answer(
        results,
        cache_time=1,          # shaxsiy — deyarli keshlamaymiz
        is_personal=True,      # natijalar foydalanuvchiga xos
        button=button,
    )
