"""Bot nomi va tavsiflarini Bot API orqali barcha tillarda o'rnatadi.

Ishga tushirish (bir marta yetarli):
    python set_bot_info.py

Rasmlarni esa @BotFather orqali qo'lda yuklash kerak:
    /setuserpic  -> assets/botpic.png (512x512)
    Edit Bot -> Edit Description Picture -> assets/description.png (640x360)

Eslatma: bot nomini (setMyName) Telegram kuniga juda kam marta
o'zgartirishga ruxsat beradi — xato bersa, qolganlari baribir o'rnatiladi.
"""
import asyncio

NAME = "Karta Bot 💳"

# None — standart (boshqa barcha tillar uchun fallback, o'zbekcha)
# Qisqa tavsif (About) — eng ko'pi 120 belgi
SHORT_DESCRIPTIONS = {
    None: "🔐 Bank kartalaringizni shifrlab saqlaydi. PIN-himoya, inline qidiruv, 8 til. Kartalaringiz — bitta xavfsiz joyda!",
    "uz": "🔐 Bank kartalaringizni shifrlab saqlaydi. PIN-himoya, inline qidiruv, 8 til. Kartalaringiz — bitta xavfsiz joyda!",
    "ru": "🔐 Храню банковские карты в зашифрованном виде. PIN-защита, инлайн-поиск, 8 языков. Все карты — в одном месте!",
    "en": "🔐 Keeps your bank cards encrypted. PIN protection, inline search, 8 languages. All your cards in one safe place!",
    "kk": "🔐 Банк карталарыңызды шифрлап сақтайды. PIN-қорғаныс, инлайн іздеу, 8 тіл. Барлық карталар — бір қауіпсіз жерде!",
    "ky": "🔐 Банк карталарыңызды шифрлеп сактайт. PIN-коргоо, инлайн издөө, 8 тил. Бардык карталар — бир коопсуз жерде!",
    "tg": "🔐 Кортҳои бонкиро рамзгузорӣ карда нигоҳ медорад. Ҳимояи PIN, ҷустуҷӯи inline, 8 забон. Ҳама кортҳо дар як ҷо!",
    "tr": "🔐 Banka kartlarınızı şifreli saklar. PIN koruması, satır içi arama, 8 dil. Tüm kartlarınız tek güvenli yerde!",
}

# To'liq tavsif (Start bosishdan oldin ko'rinadi) — eng ko'pi 512 belgi
_DESC_UZ = """💳 Karta Bot — bank kartalaringiz uchun xavfsiz hamyon.

🔐 Karta raqamlari shifrlangan holda saqlanadi
📌 PIN-kod himoyasi — 5 ta xato urinishdan so'ng vaqtincha bloklanadi
🔎 Inline: istalgan chatda @tezkartabot yozing — kartani bir zumda yuboring
✏️ Qo'shish, tahrirlash, o'chirish — to'liq boshqaruv
💾 Zaxira nusxa: eksport va import
🌍 8 til: o'zbek, rus, ingliz, qozoq, qirg'iz, tojik, turk

Boshlash uchun pastdagi Start tugmasini bosing 👇"""

DESCRIPTIONS = {
    None: _DESC_UZ,
    "uz": _DESC_UZ,
    "ru": """💳 Karta Bot — безопасный кошелёк для ваших банковских карт.

🔐 Номера карт хранятся только в зашифрованном виде
📌 PIN-код: после 5 неверных попыток — временная блокировка
🔎 Инлайн: напишите @tezkartabot в любом чате и мгновенно отправьте карту
✏️ Добавление, редактирование, удаление карт
💾 Резервная копия: экспорт и импорт
🌍 8 языков: узбекский, русский, английский, казахский, киргизский, таджикский, турецкий

Нажмите Start, чтобы начать 👇""",
    "en": """💳 Karta Bot — a secure wallet for your bank cards.

🔐 Card numbers are stored encrypted only
📌 PIN protection: temporary lock after 5 wrong attempts
🔎 Inline: type @tezkartabot in any chat to send a card instantly
✏️ Add, edit and delete cards
💾 Backup: export and import
🌍 8 languages: Uzbek, Russian, English, Kazakh, Kyrgyz, Tajik, Turkish

Tap Start to begin 👇""",
    "kk": """💳 Karta Bot — банк карталарыңыз үшін қауіпсіз әмиян.

🔐 Карта нөмірлері тек шифрланған түрде сақталады
📌 PIN-қорғаныс: 5 қате әрекеттен кейін уақытша бұғатталады
🔎 Инлайн: кез келген чатта @tezkartabot деп жазып, картаны жіберіңіз
💾 Резервтік көшірме: экспорт және импорт
🌍 8 тіл қолдауы

Бастау үшін Start басыңыз 👇""",
    "ky": """💳 Karta Bot — банк карталарыңыз үчүн коопсуз капчык.

🔐 Карта номерлери шифрленген түрдө гана сакталат
📌 PIN-коргоо: 5 ката аракеттен кийин убактылуу бөгөттөлөт
🔎 Инлайн: каалаган чатта @tezkartabot деп жазып, картаны жөнөтүңүз
💾 Резервдик көчүрмө: экспорт жана импорт
🌍 8 тил колдоосу

Баштоо үчүн Start басыңыз 👇""",
    "tg": """💳 Karta Bot — ҳамёни бехатар барои кортҳои бонкии шумо.

🔐 Рақамҳои корт танҳо дар шакли рамзгузоришуда нигоҳ дошта мешаванд
📌 Ҳимояи PIN: пас аз 5 кӯшиши нодуруст муваққатан баста мешавад
🔎 Inline: дар ҳар чат @tezkartabot нависед ва кортро фиристед
💾 Нусхаи эҳтиётӣ: содирот ва воридот
🌍 8 забон

Барои оғоз Start-ро пахш кунед 👇""",
    "tr": """💳 Karta Bot — banka kartlarınız için güvenli bir cüzdan.

🔐 Kart numaraları yalnızca şifrelenmiş olarak saklanır
📌 PIN koruması: 5 yanlış denemeden sonra geçici kilitlenir
🔎 Satır içi: herhangi bir sohbette @tezkartabot yazın, kartı anında gönderin
✏️ Kart ekleme, düzenleme, silme
💾 Yedekleme: dışa ve içe aktarma
🌍 8 dil desteği

Başlamak için Start'a dokunun 👇""",
}


def validate():
    assert len(NAME) <= 64, f"Nom {len(NAME)} belgi (>64)"
    for code, text in SHORT_DESCRIPTIONS.items():
        assert len(text) <= 120, f"Qisqa tavsif [{code}]: {len(text)} belgi (>120)"
    for code, text in DESCRIPTIONS.items():
        assert len(text) <= 512, f"Tavsif [{code}]: {len(text)} belgi (>512)"


async def main():
    from aiogram import Bot
    from config import BOT_TOKEN

    validate()
    bot = Bot(BOT_TOKEN)
    try:
        try:
            await bot.set_my_name(NAME)
            print(f"✅ Nom: {NAME}")
        except Exception as e:  # noqa: BLE001 — nom cheklovi qolganlarga to'siq emas
            print(f"⚠️ Nom o'rnatilmadi (Telegram cheklovi bo'lishi mumkin): {e}")

        for code, text in SHORT_DESCRIPTIONS.items():
            await bot.set_my_short_description(text, language_code=code)
            print(f"✅ Qisqa tavsif [{code or 'standart'}]")

        for code, text in DESCRIPTIONS.items():
            await bot.set_my_description(text, language_code=code)
            print(f"✅ Tavsif [{code or 'standart'}]")

        print("\n🎉 Tayyor! Rasmlarni @BotFather orqali qo'lda yuklang (yuqoridagi izohga qarang).")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
