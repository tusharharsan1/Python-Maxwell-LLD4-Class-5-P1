"""Tests for Problem 1: Low Stock Flag.

Run them from the folder that contains `app/`:

    pytest

Each test has a long name that says what it checks. If a test fails,
read its name and the message under it: they tell you what to fix.
"""
import copy
import inspect

import pytest

from app.services import product_service
from app.services.product_service import PRODUCTS, ProductService

# The products exactly as they must be at the start (see the README table).
ORIGINAL_PRODUCTS = {
    1: {"id": 1, "title": "Essence Mascara Lash Princess", "price": 9.99, "stock": 99},
    2: {"id": 2, "title": "Eyeshadow Palette with Mirror", "price": 19.99, "stock": 6},
    3: {"id": 3, "title": "Powder Canister", "price": 14.99, "stock": 10},
    4: {"id": 4, "title": "Red Lipstick", "price": 12.99, "stock": 0},
    5: {"id": 5, "title": "Red Nail Polish", "price": 8.99, "stock": 52},
}

# Which of the five products is low stock (stock below 10).
EXPECTED_FLAGS = {1: False, 2: True, 3: False, 4: True, 5: False}


@pytest.fixture
def service():
    return ProductService()


def make_product(stock, **extra):
    """A small product to feed into the service."""
    product = {"id": 100, "title": "Test Product", "price": 5.0, "stock": stock}
    product.update(extra)
    return product


# ---------------------------------------------------------------------------
# Task 1: _with_flags  (the rule)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stock", [0, 1, 5, 9])
def test_stock_below_the_limit_is_low_stock(service, stock):
    result = service._with_flags(make_product(stock))
    assert result["low_stock"] is True, f"stock {stock} is below 10, so low_stock must be True"


@pytest.mark.parametrize("stock", [10, 11, 52, 1000])
def test_stock_at_or_above_the_limit_is_not_low_stock(service, stock):
    result = service._with_flags(make_product(stock))
    assert result["low_stock"] is False, f"stock {stock} is not below 10, so low_stock must be False"


def test_low_stock_is_a_real_true_or_false(service):
    assert service._with_flags(make_product(3))["low_stock"] is True
    assert service._with_flags(make_product(50))["low_stock"] is False


def test_the_rule_uses_the_name_LOW_STOCK_LIMIT_and_not_the_number_10(service, monkeypatch):
    # The owner changes the limit to 5: now stock 5 is NOT low any more, and 4 still is.
    monkeypatch.setattr(product_service, "LOW_STOCK_LIMIT", 5)
    assert service._with_flags(make_product(4))["low_stock"] is True
    assert service._with_flags(make_product(5))["low_stock"] is False
    assert service._with_flags(make_product(9))["low_stock"] is False, (
        "with the limit at 5, stock 9 is not low. Did you write the number 10 in your code?"
    )

    # The owner changes the limit to 20: now stock 15 IS low.
    monkeypatch.setattr(product_service, "LOW_STOCK_LIMIT", 20)
    assert service._with_flags(make_product(15))["low_stock"] is True, (
        "with the limit at 20, stock 15 is low. Did you write the number 10 in your code?"
    )
    assert service._with_flags(make_product(20))["low_stock"] is False


# ---------------------------------------------------------------------------
# Task 1: _with_flags  (a copy, not a change)
# ---------------------------------------------------------------------------

def test_result_has_everything_from_the_product_plus_the_flag(service):
    product = make_product(3)
    result = service._with_flags(product)
    assert result == {**product, "low_stock": True}


def test_extra_keys_of_the_product_are_kept(service):
    product = make_product(3, brand="Essence", tags=["beauty", "mascara"])
    result = service._with_flags(product)
    assert result["brand"] == "Essence"
    assert result["tags"] == ["beauty", "mascara"]
    assert result["low_stock"] is True


def test_the_dictionary_that_was_passed_in_is_not_changed(service):
    product = make_product(3)
    before = copy.deepcopy(product)
    service._with_flags(product)
    assert product == before, "_with_flags must not change the dictionary it receives"
    assert "low_stock" not in product


def test_the_result_is_a_new_dictionary(service):
    product = make_product(3)
    result = service._with_flags(product)
    assert result is not product, "return a NEW dictionary, not the one that was passed in"


# ---------------------------------------------------------------------------
# Task 2: get_by_id
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("product_id", [1, 2, 3, 4, 5])
def test_get_by_id_returns_the_product_with_the_right_flag(service, product_id):
    result = service.get_by_id(product_id)
    expected = {**ORIGINAL_PRODUCTS[product_id], "low_stock": EXPECTED_FLAGS[product_id]}
    assert result == expected


@pytest.mark.parametrize("product_id", [0, -1, 6, 99, 1000])
def test_get_by_id_returns_none_when_there_is_no_such_product(service, product_id):
    assert service.get_by_id(product_id) is None


def test_get_by_id_does_not_change_the_stored_products(service):
    before = copy.deepcopy(PRODUCTS)
    for product_id in [1, 2, 3, 4, 5, 99]:
        service.get_by_id(product_id)
    assert PRODUCTS == before, "get_by_id must not change PRODUCTS"
    for product in PRODUCTS.values():
        assert "low_stock" not in product, "do not store low_stock inside PRODUCTS"


def test_changing_the_result_does_not_change_the_stored_product(service):
    result = service.get_by_id(1)
    assert result is not PRODUCTS[1], "return a copy, not the stored dictionary"
    result["title"] = "Changed outside the service"
    assert PRODUCTS[1]["title"] == "Essence Mascara Lash Princess"


def test_get_by_id_reads_the_products_as_they_are_now(service, monkeypatch):
    # A product added later must be found...
    monkeypatch.setitem(PRODUCTS, 77, make_product(2, id=77, title="Late Arrival"))
    late = service.get_by_id(77)
    assert late is not None, "a product added to PRODUCTS must be found"
    assert late["title"] == "Late Arrival"
    assert late["low_stock"] is True

    # ...and a changed stock must change the flag.
    monkeypatch.setitem(PRODUCTS[1], "stock", 3)
    assert service.get_by_id(1)["low_stock"] is True


def test_get_by_id_follows_the_limit_too(service, monkeypatch):
    monkeypatch.setattr(product_service, "LOW_STOCK_LIMIT", 7)
    assert service.get_by_id(2)["low_stock"] is True    # stock 6 is below 7
    assert service.get_by_id(3)["low_stock"] is False   # stock 10 is not


def test_get_by_id_uses_with_flags_so_the_rule_is_in_one_place(service, monkeypatch):
    monkeypatch.setattr(ProductService, "_with_flags", lambda self, product: {"marker": product["id"]})
    assert service.get_by_id(1) == {"marker": 1}, (
        "get_by_id must call self._with_flags(...) and return what it returns"
    )


# ---------------------------------------------------------------------------
# The parts that must stay as they were
# ---------------------------------------------------------------------------

def test_exists_still_works(service):
    assert service.exists(1) is True
    assert service.exists(5) is True
    assert service.exists(99) is False


def test_method_names_and_parameters_are_unchanged():
    with_flags = inspect.signature(ProductService._with_flags)
    get_by_id = inspect.signature(ProductService.get_by_id)
    assert list(with_flags.parameters) == ["self", "product"]
    assert list(get_by_id.parameters) == ["self", "product_id"]


def test_the_products_dictionary_and_the_limit_were_not_edited():
    assert PRODUCTS == ORIGINAL_PRODUCTS, "PRODUCTS must stay exactly as it was given"
    assert product_service.LOW_STOCK_LIMIT == 10
