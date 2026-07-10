"""database/db.py — shifrlash va CRUD uchun testlar.

Test o'z ENCRYPTION_KEY va vaqtinchalik bazasini ishlatadi — haqiqiy
`cards.db` yoki haqiqiy kalitga tegmaydi.
"""
import os
import sys
import tempfile
import unittest

from cryptography.fernet import Fernet # pyright: ignore[reportMissingImports]

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# database import qilinishidan OLDIN muhitni sozlaymiz (config shu yerda o'qiydi).
os.environ["BOT_TOKEN"] = "test:token"
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
_TMP_DB = os.path.join(tempfile.gettempdir(), "karta_test.db")
os.environ["DB_PATH"] = _TMP_DB

import database as db  # noqa: E402


class DBTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if os.path.exists(_TMP_DB):
            os.remove(_TMP_DB)  # har test uchun toza baza
        await db.init_db()

    async def test_add_and_get_roundtrip(self):
        await db.add_card(1, "Ish", "8600123456789012", "Ali Valiyev")
        cards = await db.get_cards(1)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["number"], "8600123456789012")  # deshifrlangan
        self.assertEqual(cards[0]["name"], "Ish")
        self.assertEqual(cards[0]["holder"], "Ali Valiyev")

    async def test_number_encrypted_at_rest(self):
        await db.add_card(1, "Ish", "8600123456789012", "Ali")
        # Bazadagi xom qiymat ochiq raqamni O'Z ICHIGA OLMASLIGI kerak.
        import aiosqlite # type: ignore
        async with aiosqlite.connect(_TMP_DB) as raw:
            async with raw.execute("SELECT number FROM cards") as cur:
                (stored,) = await cur.fetchone()
        self.assertNotIn("8600123456789012", stored)

    async def test_cards_isolated_per_user(self):
        await db.add_card(1, "A", "8600000000000001", "X")
        await db.add_card(2, "B", "8600000000000002", "Y")
        self.assertEqual(len(await db.get_cards(1)), 1)
        self.assertEqual(len(await db.get_cards(2)), 1)

    async def test_update_number_reencrypts(self):
        await db.add_card(1, "Ish", "8600000000000001", "X")
        cid = (await db.get_cards(1))[0]["id"]
        await db.update_number(1, cid, "9860111122223333")
        self.assertEqual((await db.get_card(1, cid))["number"], "9860111122223333")

    async def test_delete(self):
        await db.add_card(1, "Ish", "8600000000000001", "X")
        cid = (await db.get_cards(1))[0]["id"]
        await db.delete_card(1, cid)
        self.assertEqual(await db.get_cards(1), [])

    async def test_name_and_number_lookup(self):
        await db.add_card(1, "Ish", "8600000000000001", "X")
        self.assertTrue(await db.name_exists(1, "ish"))  # katta-kichik harf sezmaydi
        self.assertFalse(await db.name_exists(1, "yoq"))
        self.assertIsNotNone(await db.find_by_number(1, "8600000000000001"))

    async def test_lang_default_and_set(self):
        self.assertEqual(await db.get_lang(999), "uz")  # standart
        await db.set_lang(999, "ru")
        self.assertEqual(await db.get_lang(999), "ru")

    async def test_pin_set_verify_clear(self):
        await db.set_pin(5, "1234")
        self.assertTrue(await db.has_pin(5))
        self.assertTrue(await db.verify_pin(5, "1234"))
        self.assertFalse(await db.verify_pin(5, "0000"))
        await db.clear_pin(5)
        self.assertFalse(await db.has_pin(5))


if __name__ == "__main__":
    unittest.main()
