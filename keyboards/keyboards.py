"""Barcha klaviaturalar shu yerda yig'ilgan."""
from aiogram.types import ( # type: ignore
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, CopyTextButton,
)

from utils.text import only_digits

from locales import t, LANGUAGES


def main_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_add"))],
            [KeyboardButton(text=t(lang, "menu_cards"))],
            [KeyboardButton(text=t(lang, "menu_settings"))],
        ],
        resize_keyboard=True,
    )


def lang_kb():
    rows, row = [], []
    for code, title in LANGUAGES:
        row.append(InlineKeyboardButton(text=title, callback_data=f"lang:{code}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def flow_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "back"), callback_data="add_back"),
        InlineKeyboardButton(text=t(lang, "cancel_btn"), callback_data="add_cancel"),
    ]])


def noname_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "save_noname"), callback_data="save_noname")],
        [InlineKeyboardButton(text=t(lang, "cancel_btn"), callback_data="add_cancel")],
    ])


def luhn_kb(lang, edit=False):
    """Luhn tekshiruvidan o'tmagan raqam uchun: baribir saqlash / bekor qilish.

    `edit=True` — tahrirlash oqimida (boshqa callback ishlatiladi).
    """
    ok = "eluhn_ok" if edit else "luhn_ok"
    cancel = "edit_cancel" if edit else "add_cancel"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "luhn_save_anyway"), callback_data=ok)],
        [InlineKeyboardButton(text=t(lang, "cancel_btn"), callback_data=cancel)],
    ])


def card_view_kb(lang, card_id, index, total, readonly=False, owner_id=None, number=None):
    """Karusel klaviaturasi: ◀️ N/M ▶️ (aylanma) + Nusxa + Tahrirlash / O'chirish.

    `readonly=True` (guruh chatlari) — Tahrirlash/O'chirish tugmalari yo'q,
    varaqlash tugmalariga karta egasining id'si biriktiriladi (nav:i:owner).
    `number` berilsa, raqamni bir bosishda nusxalash tugmasi qo'shiladi.
    """
    rows = []
    if total > 1:
        prev_i = (index - 1) % total
        next_i = (index + 1) % total
        suffix = f":{owner_id}" if readonly and owner_id is not None else ""
        rows.append([
            InlineKeyboardButton(text="◀️", callback_data=f"nav:{prev_i}{suffix}"),
            InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="noop"),
            InlineKeyboardButton(text="▶️", callback_data=f"nav:{next_i}{suffix}"),
        ])
    if number:
        rows.append([InlineKeyboardButton(
            text=t(lang, "copy_btn"),
            copy_text=CopyTextButton(text=only_digits(number)),
        )])
    if not readonly:
        rows.append([InlineKeyboardButton(text=t(lang, "edit_btn"), callback_data=f"edit:{card_id}")])
        rows.append([InlineKeyboardButton(text=t(lang, "delete"), callback_data=f"delask:{card_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def edit_menu_kb(lang, card_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "edit_name_btn"), callback_data=f"efld:name:{card_id}")],
        [InlineKeyboardButton(text=t(lang, "edit_holder_btn"), callback_data=f"efld:holder:{card_id}")],
        [InlineKeyboardButton(text=t(lang, "edit_number_btn"), callback_data=f"efld:number:{card_id}")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data=f"delno:{card_id}")],
    ])


def delete_confirm_kb(lang, card_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "no"), callback_data=f"delno:{card_id}"),
        InlineKeyboardButton(text=t(lang, "yes"), callback_data=f"delyes:{card_id}"),
    ]])


def pin_manage_kb(lang):
    """Joriy PIN to'g'ri kiritilgach ochiladigan menyu: o'zgartirish yoki o'chirish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "pin_change_btn"), callback_data="pin:change")],
        [InlineKeyboardButton(text=t(lang, "pin_remove_btn"), callback_data="pin:remove")],
    ])


def inline_try_kb(lang):
    """«Yuborib ko'ring» — bosilganda chat tanlanadi va `@bot ` avtomat yoziladi.

    `switch_inline_query=""` — bo'sh so'rov bilan inline rejimni ochadi.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "inline_try_btn"), switch_inline_query=""),
    ]])


def settings_kb(lang, has_pin, unlocked=False):
    """Sozlamalar menyusi: til, PIN, zaxira nusxa.

    Qulflash tugmasi yo'q — qulf 1 daqiqadan keyin avtomatik yopiladi
    (`UNLOCK_TTL`, security.py).
    """
    pin_btn = "set_pin_btn" if has_pin else "set_pin_on_btn"
    rows = [
        [InlineKeyboardButton(text=t(lang, "set_lang_btn"), callback_data="set:lang")],
        [InlineKeyboardButton(text=t(lang, pin_btn), callback_data="set:pin")],
        [
            InlineKeyboardButton(text=t(lang, "set_export_btn"), callback_data="set:export"),
            InlineKeyboardButton(text=t(lang, "set_import_btn"), callback_data="set:import"),
        ],
        [InlineKeyboardButton(text=t(lang, "set_security_btn"), callback_data="set:security")],
        [InlineKeyboardButton(text=t(lang, "feedback_btn"), url="https://t.me/Ibrohim_qobilov_aloqabot")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
