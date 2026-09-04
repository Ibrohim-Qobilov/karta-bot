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
)

import database as db
from locales import t
from utils.text import mask, card_brand

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
        number = f"<code>{mask(c['number'])}</code>"  # bosilsa nusxalanadi
        # Yuborilganda: karta turi (bo'lsa) + raqam — chatdan tashqarida ko'rinmasligi uchun to'liq spoiler bilan
        content = f"{brand}\n{number}" if brand else number
        text = f"<tg-spoiler>{content}</tg-spoiler>"
        results.append(InlineQueryResultArticle(
            id=str(c["id"]),
            title=c["name"],
            description=(brand + " · " if brand else "") + "•••• " + c["number"][-4:],
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML",
            ),
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
