"""Matn yordamchilari."""
import html
import re

# Menyu tugmalari boshidagi emojilar (FSM ichida menyu bosilganini aniqlash uchun)
MENU_EMOJIS = ("➕", "📋", "👥", "⚙️")


def mask(number):
    """Raqamni 4 talik bo'lib ajratadi: 8600123456789012 -> 8600 1234 5678 9012."""
    digits = re.sub(r"\D", "", number)
    return " ".join(digits[i:i + 4] for i in range(0, len(digits), 4))


def only_digits(text):
    return re.sub(r"\D", "", text or "")


def luhn_valid(number):
    """Luhn algoritmi bo'yicha karta raqamini tekshiradi (chop xatolarini ushlaydi).

    Uzcard/Humo/Visa/Mastercard raqamlari ISO 7812 bo'yicha shu nazorat
    raqamiga ega. Faqat raqamlar hisobga olinadi.
    """
    d = [int(c) for c in re.sub(r"\D", "", number or "")]
    if not d:
        return False
    checksum = 0
    for i, digit in enumerate(reversed(d)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def card_brand(number):
    """Karta raqamining boshiga qarab to'lov tizimini aniqlaydi.

    Aniqlab bo'lmasa None qaytaradi.
    """
    d = re.sub(r"\D", "", number)
    if d.startswith("9860"):
        return "🟢 Humo"
    if d.startswith("8600") or d.startswith("5614"):
        return "🔵 Uzcard"
    if d.startswith("4"):
        return "💠 Visa"
    if d[:2] in {"51", "52", "53", "54", "55"} or (
        len(d) >= 4 and d[:4].isdigit() and 2221 <= int(d[:4]) <= 2720
    ):
        return "🟠 Mastercard"
    if d.startswith("62"):
        return "🟣 UnionPay"
    return None


def card_text(c):
    """Karta matni (HTML). Raqam <code> ichida — bosilsa nusxalanadi.

    Nom/egasi HTML uchun ekranlanadi (< > & belgilaridan himoya).
    Ishlatilganda `parse_mode="HTML"` bilan yuborilishi shart.
    """
    name = html.escape(c["name"])
    holder = html.escape(c["holder"] or "-")
    brand = card_brand(c["number"])
    title = f"💳 {name}"
    if brand:
        title += f" · {brand}"
    return f"{title}\n{holder}\n<code>{mask(c['number'])}</code>"
