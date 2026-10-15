import copy
import inspect
import os
import sys
import unittest
from unittest.mock import patch

# Lets this file run directly (python tests/test_product_service.py) from any folder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import product_service
from app.services.product_service import PRODUCTS, ProductService

# ---------------------------------------------------------------------------
# Test data — the products exactly as they must be at the start (README table)
# ---------------------------------------------------------------------------

ORIGINAL_PRODUCTS = {
    1: {"id": 1, "title": "Essence Mascara Lash Princess", "price": 9.99, "stock": 99},
    2: {"id": 2, "title": "Eyeshadow Palette with Mirror", "price": 19.99, "stock": 6},
    3: {"id": 3, "title": "Powder Canister", "price": 14.99, "stock": 10},
    4: {"id": 4, "title": "Red Lipstick", "price": 12.99, "stock": 0},
    5: {"id": 5, "title": "Red Nail Polish", "price": 8.99, "stock": 52},
}

# Which of the five products is low stock (stock below 10).
EXPECTED_FLAGS = {1: False, 2: True, 3: False, 4: True, 5: False}


# ---------------------------------------------------------------------------
# Helper — builds a small product to feed into the service
# ---------------------------------------------------------------------------

def _make_product(stock, **extra):
    """Creates a product dictionary with the given stock (and any extra keys)."""
    product = {"id": 100, "title": "Test Product", "price": 5.0, "stock": stock}
    product.update(extra)
    return product


# ===========================================================================
# Test Suite 1 — Task 1: _with_flags (the low stock rule)
# ===========================================================================

class TestLowStockRule(unittest.TestCase):
    """Tests that _with_flags applies the 'stock below the limit' rule correctly."""

    def setUp(self):
        self.service = ProductService()

    def test_stock_below_the_limit_is_low_stock(self):
        """Stock 0, 1, 5 and 9 are below 10, so low_stock must be True."""
        for stock in [0, 1, 5, 9]:
            with self.subTest(stock=stock):
                result = self.service._with_flags(_make_product(stock))
                self.assertIs(result["low_stock"], True)

    def test_stock_at_or_above_the_limit_is_not_low_stock(self):
        """Stock 10, 11, 52 and 1000 are not below 10, so low_stock must be False."""
        for stock in [10, 11, 52, 1000]:
            with self.subTest(stock=stock):
                result = self.service._with_flags(_make_product(stock))
                self.assertIs(result["low_stock"], False)

    def test_stock_exactly_equal_to_the_limit_is_not_low_stock(self):
        """The boundary: stock 10 is NOT low stock (below 10 means strictly less)."""
        result = self.service._with_flags(_make_product(10))
        self.assertIs(result["low_stock"], False)

    def test_low_stock_is_a_real_true_or_false(self):
        """The flag must be the real True/False, not 1/0 or text."""
        self.assertIs(self.service._with_flags(_make_product(3))["low_stock"], True)
        self.assertIs(self.service._with_flags(_make_product(50))["low_stock"], False)

    def test_rule_uses_the_name_low_stock_limit_not_the_number_10(self):
        """
        The owner changes the limit. The rule must follow the NAME LOW_STOCK_LIMIT.
        Catches students who wrote the number 10 directly in the code.
        """
        with patch.object(product_service, "LOW_STOCK_LIMIT", 5):
            self.assertIs(self.service._with_flags(_make_product(4))["low_stock"], True)
            self.assertIs(self.service._with_flags(_make_product(5))["low_stock"], False)
            # Anti-bypass: with the limit at 5, stock 9 is NOT low any more.
            self.assertIs(self.service._with_flags(_make_product(9))["low_stock"], False)

        with patch.object(product_service, "LOW_STOCK_LIMIT", 20):
            # Anti-bypass: with the limit at 20, stock 15 IS low.
            self.assertIs(self.service._with_flags(_make_product(15))["low_stock"], True)
            self.assertIs(self.service._with_flags(_make_product(20))["low_stock"], False)


# ===========================================================================
# Test Suite 2 — Task 1: _with_flags (a copy, not a change)
# ===========================================================================

class TestWithFlagsReturnsACopy(unittest.TestCase):
    """Tests that _with_flags returns a NEW dictionary and never changes the input."""

    def setUp(self):
        self.service = ProductService()

    def test_result_has_everything_from_the_product_plus_the_flag(self):
        """The result must be the product's keys plus exactly one more: low_stock."""
        product = _make_product(3)
        result = self.service._with_flags(product)
        self.assertEqual(result, {**product, "low_stock": True})

    def test_extra_keys_of_the_product_are_kept(self):
        """
        Keys that are not part of the README (like brand) must survive.
        Catches students who rebuild the dictionary from only the four known keys.
        """
        product = _make_product(3, brand="Essence", tags=["beauty", "mascara"])
        result = self.service._with_flags(product)
        self.assertEqual(result["brand"], "Essence")
        self.assertEqual(result["tags"], ["beauty", "mascara"])
        self.assertIs(result["low_stock"], True)

    def test_the_dictionary_that_was_passed_in_is_not_changed(self):
        """After the call, the product that was passed in must be exactly as before."""
        product = _make_product(3)
        before = copy.deepcopy(product)
        self.service._with_flags(product)
        self.assertEqual(product, before)
        self.assertNotIn("low_stock", product)

    def test_the_result_is_a_new_dictionary(self):
        """The result must not be the same object that was passed in."""
        product = _make_product(3)
        result = self.service._with_flags(product)
        self.assertIsNot(result, product)


# ===========================================================================
# Test Suite 3 — Task 2: get_by_id
# ===========================================================================

class TestGetById(unittest.TestCase):
    """End-to-end tests for the get_by_id service method."""

    def setUp(self):
        self.service = ProductService()

    # --- Happy path ---

    def test_every_product_comes_back_with_the_right_flag(self):
        """Each of the five products must come back with its fields and the right flag."""
        for product_id in [1, 2, 3, 4, 5]:
            with self.subTest(product_id=product_id):
                result = self.service.get_by_id(product_id)
                expected = {**ORIGINAL_PRODUCTS[product_id], "low_stock": EXPECTED_FLAGS[product_id]}
                self.assertEqual(result, expected)

    def test_get_by_id_reads_the_products_as_they_are_now(self):
        """
        A product added later must be found, and a changed stock must change the flag.
        Catches students who copied the data once, or who hard-coded the answers.
        """
        late_product = _make_product(2, id=77, title="Late Arrival")
        with patch.dict(PRODUCTS, {77: late_product}):
            result = self.service.get_by_id(77)
            self.assertIsNotNone(result)
            self.assertEqual(result["title"], "Late Arrival")
            self.assertIs(result["low_stock"], True)

        with patch.dict(PRODUCTS[1], {"stock": 3}):
            self.assertIs(self.service.get_by_id(1)["low_stock"], True)

    def test_get_by_id_follows_the_limit_too(self):
        """When the limit changes, get_by_id must give the new answer."""
        with patch.object(product_service, "LOW_STOCK_LIMIT", 7):
            self.assertIs(self.service.get_by_id(2)["low_stock"], True)    # stock 6 is below 7
            self.assertIs(self.service.get_by_id(3)["low_stock"], False)   # stock 10 is not

    def test_get_by_id_uses_with_flags_so_the_rule_is_in_one_place(self):
        """
        get_by_id must call self._with_flags(...) and return what it returns.
        Catches students who copy the rule into a second place.
        """
        fake = lambda self, product: {"marker": product["id"]}
        with patch.object(ProductService, "_with_flags", fake):
            self.assertEqual(self.service.get_by_id(1), {"marker": 1})

    # --- Missing products ---

    def test_get_by_id_returns_none_when_there_is_no_such_product(self):
        """Ids that are not in PRODUCTS (even 0 and negative) must give None."""
        for product_id in [0, -1, 6, 99, 1000]:
            with self.subTest(product_id=product_id):
                self.assertIsNone(self.service.get_by_id(product_id))

    # --- The stored data must stay as it is ---

    def test_get_by_id_does_not_change_the_stored_products(self):
        """
        After many calls, PRODUCTS must be exactly as before, with no low_stock key inside.
        Catches students who write the flag into the stored dictionaries.
        """
        before = copy.deepcopy(PRODUCTS)
        for product_id in [1, 2, 3, 4, 5, 99]:
            self.service.get_by_id(product_id)
        self.assertEqual(PRODUCTS, before)
        for product in PRODUCTS.values():
            self.assertNotIn("low_stock", product)

    def test_changing_the_result_does_not_change_the_stored_product(self):
        """The result must be a copy: changing it must not change PRODUCTS."""
        result = self.service.get_by_id(1)
        self.assertIsNot(result, PRODUCTS[1])
        result["title"] = "Changed outside the service"
        self.assertEqual(PRODUCTS[1]["title"], "Essence Mascara Lash Princess")


# ===========================================================================
# Test Suite 4 — The parts that must stay as they were
# ===========================================================================

class TestPartsThatMustStayTheSame(unittest.TestCase):
    """Tests that the finished example and the given data were not edited."""

    def setUp(self):
        self.service = ProductService()

    def test_exists_still_works(self):
        """The finished example method must still answer True/False correctly."""
        self.assertIs(self.service.exists(1), True)
        self.assertIs(self.service.exists(5), True)
        self.assertIs(self.service.exists(99), False)

    def test_method_names_and_parameters_are_unchanged(self):
        """Method names and parameter names must stay as they were given."""
        with_flags = inspect.signature(ProductService._with_flags)
        get_by_id = inspect.signature(ProductService.get_by_id)
        self.assertEqual(list(with_flags.parameters), ["self", "product"])
        self.assertEqual(list(get_by_id.parameters), ["self", "product_id"])

    def test_the_products_dictionary_and_the_limit_were_not_edited(self):
        """PRODUCTS and LOW_STOCK_LIMIT must be exactly as they were given."""
        self.assertEqual(PRODUCTS, ORIGINAL_PRODUCTS)
        self.assertEqual(product_service.LOW_STOCK_LIMIT, 10)


# ===========================================================================
# Run all tests
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
