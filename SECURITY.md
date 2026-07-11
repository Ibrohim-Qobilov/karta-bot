# Xavfsizlik siyosati / Security Policy

Bu bot bank karta ma'lumotlarini saqlaydi, shuning uchun xavfsizlik birinchi
o'rinda turadi. Quyida qanday ma'lumot saqlanishi, u qanday himoyalanishi va
zaifliklarni qanday xabar qilish tartibi keltirilgan.

> 📄 Foydalanuvchilar uchun ommaviy maxfiylik siyosati:
> [telegra.ph/Karta-Bot--Maxfiylik-siyosati-07-11](https://telegra.ph/Karta-Bot--Maxfiylik-siyosati-07-11)

## Qanday ma'lumot saqlanadi

| Ma'lumot | Holati |
|---|---|
| Karta raqami | **Shifrlangan** (Fernet — AES-128-CBC + HMAC-SHA256) |
| Karta nomi (label) | Ochiq matn |
| Karta egasi (holder) | Ochiq matn |
| Foydalanuvchi tili | Ochiq matn |
| PIN-kod | **Tuzlangan SHA-256 hash** (`user_id:pin`), ochiq saqlanmaydi |

**Saqlanmaydi:** CVV/CVC, amal muddati, foydalanuvchi paroli, Telegram
ma'lumotlari. Kod faqat raqam, nom va egasini saqlaydi.

## Shifrlash

- Karta raqamlari bazaga yozishdan oldin
  [`cryptography.fernet`](https://cryptography.io/) yordamida shifrlanadi
  (`database/db.py` — `add_card`, `update_number`, `get_cards`).
- Kalit `ENCRYPTION_KEY` muhit o'zgaruvchisidan olinadi (`config.py`) va
  **hech qachon kodga yoki gitga yozilmaydi**.
- Deshifrlab bo'lmagan yozuvlar (`InvalidToken`) jimgina o'tkazib yuboriladi —
  noto'g'ri kalit bilan boshqa foydalanuvchi ma'lumotini ochib bo'lmaydi.

## Kirishni cheklash (access control)

- **PIN himoyasi** — foydalanuvchi 4 xonali PIN o'rnatishi mumkin
  (Sozlamalar → PIN). Kartalarni ko'rishdan oldin PIN so'raladi.
- **Avto-qulf** — PIN bir marta kiritilgach 60 soniya amal qiladi
  (`UNLOCK_TTL`, `handlers/security.py`), keyin qayta so'raladi.
- **Brute-force himoya** — 5 marta noto'g'ri urinishdan so'ng 60 soniyaga
  bloklanadi (`MAX_PIN_TRIES`, `PIN_BLOCK`).
- Qulf holati faqat xotirada saqlanadi — bot qayta ishga tushsa, hammasi
  qaytadan qulflanadi.

## Ma'lum cheklovlar (foydalanuvchi bilishi kerak)

- **Zaxira (backup) fayli** karta raqamlarini **ochiq JSON** ko'rinishida
  o'z ichiga oladi (`handlers/backup.py`). Uni birovga yubormaslik kerak —
  bot eksport faylida bu haqda ogohlantiradi.
- **Inline rejim** (`@bot` orqali yuborish) PIN so'ramaydi va yuborilgan
  karta o'sha chatda ochiq ko'rinadi. Bu Telegram cheklovi.
- Telegram akkauntiga yoki qurilmaga kirish huquqiga ega har kim saqlangan
  kartalarni ko'ra oladi.

## Deployment tavsiyalari

- `ENCRYPTION_KEY` va `BOT_TOKEN`ni faqat `.env` da saqlang; `.gitignore`
  allaqachon `.env` ni chiqarib tashlaydi — buni buzmang.
- `ENCRYPTION_KEY`ni yo'qotmang: kalit yo'qolsa, saqlangan raqamlarni
  deshifrlab bo'lmaydi (tiklash imkonsiz).
- Baza fayli (`cards.db`) va `.env` ga fayl-tizim ruxsatlarini cheklang
  (masalan `chmod 600`).
- Kalitni almashtirsangiz (rotation), eski ma'lumotni eski kalit bilan
  deshifrlab, yangisi bilan qayta shifrlash kerak.

## Zaiflikni xabar qilish (Reporting a vulnerability)

Zaiflik topsangiz, uni **ommaviy issue ochib emas**, maxfiy tarzda xabar qiling:

- Telegram orqali aloqa botiga yozing: [@Ibrohim_qobilov_aloqabot](https://t.me/Ibrohim_qobilov_aloqabot).
- Muammoni takrorlash bosqichlari va ta'sirini tavsiflang.
- Tuzatilgunicha tafsilotlarni oshkor qilmang.

Javobga oqilona muddat ichida (masalan 7 kun) harakat qilinadi.
