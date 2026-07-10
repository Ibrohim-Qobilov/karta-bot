"""utils/text.py — sof funksiyalar uchun testlar (config talab qilmaydi)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text import card_brand, luhn_valid, mask, only_digits  # noqa: E402


class LuhnTest(unittest.TestCase):
    def test_valid_numbers(self):
        # Luhn bo'yicha to'g'ri raqamlar (nazorat raqami mos)
        self.assertTrue(luhn_valid("4242424242424242"))  # Visa test
        self.assertTrue(luhn_valid("8600 4954 7331 6478"))  # bo'sh joylar ham

    def test_invalid_numbers(self):
        self.assertFalse(luhn_valid("4242424242424241"))  # bitta raqam buzilgan
        self.assertFalse(luhn_valid("1234567890123456"))

    def test_empty(self):
        self.assertFalse(luhn_valid(""))
        self.assertFalse(luhn_valid(None))


class MaskTest(unittest.TestCase):
    def test_groups_of_four(self):
        self.assertEqual(mask("8600123456789012"), "8600 1234 5678 9012")

    def test_strips_non_digits(self):
        self.assertEqual(mask("8600-1234-5678-9012"), "8600 1234 5678 9012")

    def test_short(self):
        self.assertEqual(mask("860012"), "8600 12")


class OnlyDigitsTest(unittest.TestCase):
    def test_removes_symbols(self):
        self.assertEqual(only_digits("8600 1234-ab"), "86001234")

    def test_none(self):
        self.assertEqual(only_digits(None), "")


class CardBrandTest(unittest.TestCase):
    def test_uzcard(self):
        self.assertIn("Uzcard", card_brand("8600123456789012"))
        self.assertIn("Uzcard", card_brand("5614123456789012"))

    def test_humo(self):
        self.assertIn("Humo", card_brand("9860123456789012"))

    def test_visa(self):
        self.assertIn("Visa", card_brand("4278310012345678"))

    def test_mastercard(self):
        self.assertIn("Mastercard", card_brand("5486730012345678"))
        self.assertIn("Mastercard", card_brand("2223000012345678"))  # 2-diapazon

    def test_unionpay(self):
        self.assertIn("UnionPay", card_brand("6262180012345678"))

    def test_unknown(self):
        self.assertIsNone(card_brand("1234567890123456"))


if __name__ == "__main__":
    unittest.main()
