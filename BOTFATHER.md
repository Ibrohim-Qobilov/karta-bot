# 🤖 BotFather sozlamalari

Bot profilini to'liq rasmiylashtirish uchun tayyor materiallar. Matnlarni
qo'lda ko'chirish o'rniga **bitta buyruq bilan** barcha tillarda o'rnatish mumkin:

```bash
python set_bot_info.py
```

Bu skript nom, qisqa tavsif (About) va to'liq tavsifni (Description) 8 tilda —
o'zbek, rus, ingliz, qozoq, qirg'iz, tojik, turk tillarida o'rnatadi
(foydalanuvchi Telegram tiliga qarab mos matnni ko'radi).

Rasmlarni esa Telegram API orqali o'rnatib bo'lmaydi — ularni [@BotFather](https://t.me/BotFather)
orqali qo'lda yuklash kerak (quyida).

---

## 🖼 Rasmlar (`assets/` papkasida)

| Fayl | O'lchami | Qayerga |
|------|----------|---------|
| `assets/botpic.png` | 512×512 | Bot profil rasmi (avatar) |
| `assets/description.png` | 640×360 | Tavsif rasmi (Start bosishdan oldin ko'rinadi) |
| `assets/banner.png` | 1280×400 | README / kanal posti uchun banner |

**Yuklash tartibi:**

1. [@BotFather](https://t.me/BotFather) ni oching
2. `/mybots` → `@tezkartabot` ni tanlang
3. **Edit Bot** bo'limiga kiring:
   - **Edit Botpic** → `assets/botpic.png` ni yuboring
   - **Edit Description Picture** → `assets/description.png` ni yuboring

---

## ✏️ Matnlar (qo'lda kiritmoqchi bo'lsangiz)

> Barcha tillardagi variantlar `set_bot_info.py` faylida. Quyida asosiy uchtasi.

### Nom (Edit Name)

```
Karta Bot 💳
```

### Qisqa tavsif — About (Edit About, ≤120 belgi)

**O'zbekcha (standart):**
```
🔐 Bank kartalaringizni shifrlab saqlaydi. PIN-himoya, inline qidiruv, 8 til. Kartalaringiz — bitta xavfsiz joyda!
```

**Ruscha:**
```
🔐 Храню банковские карты в зашифрованном виде. PIN-защита, инлайн-поиск, 8 языков. Все карты — в одном месте!
```

**Inglizcha:**
```
🔐 Keeps your bank cards encrypted. PIN protection, inline search, 8 languages. All your cards in one safe place!
```

### To'liq tavsif — Description (Edit Description, ≤512 belgi)

**O'zbekcha (standart):**
```
💳 Karta Bot — bank kartalaringiz uchun xavfsiz hamyon.

🔐 Karta raqamlari shifrlangan holda saqlanadi
📌 PIN-kod himoyasi — 5 ta xato urinishdan so'ng vaqtincha bloklanadi
🔎 Inline: istalgan chatda @tezkartabot yozing — kartani bir zumda yuboring
✏️ Qo'shish, tahrirlash, o'chirish — to'liq boshqaruv
💾 Zaxira nusxa: eksport va import
🌍 8 til: o'zbek, rus, ingliz, qozoq, qirg'iz, tojik, turk

Boshlash uchun pastdagi Start tugmasini bosing 👇
```

---

## ⌨️ Buyruqlar (Edit Commands)

`main.py` har ishga tushganda buyruqlarni o'zi o'rnatadi. BotFather orqali
qo'lda kiritmoqchi bo'lsangiz:

```
karta - 💳 Kartalarim / My cards
card - 💳 My cards
add - ➕ Karta qo'shish / Add card
start - 🚀 Boshlash / Start
security - 🛡 Xavfsizlik / Security
```

## 🔎 Inline sozlamalari

1. `/setinline` → bot uchun placeholder matn:
   ```
   Karta nomini yozing...
   ```
2. `/setinlinefeedback` — o'zgartirish shart emas (bot foydalanmaydi)

---

## ♻️ Rasmlarni qayta yaratish

Rasmlar Python (Pillow) bilan generatsiya qilingan — `assets/generate.py`.
Ranglar, matn yoki o'lchamlarni o'zgartirib, qayta yaratish:

```bash
pip install Pillow
python assets/generate.py
```
