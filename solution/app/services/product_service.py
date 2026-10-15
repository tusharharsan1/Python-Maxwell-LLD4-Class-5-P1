"""The ProductService: the business rules for products.

This is the finished version of the problem.
"""

# The shop owner's rule uses this number. Always use the name, never the number 10.
LOW_STOCK_LIMIT = 10

# The "database" for this problem: a dictionary that lives in memory.
# Do NOT change it. (Do not add a "low_stock" key into these dictionaries.)
PRODUCTS = {
    1: {"id": 1, "title": "Essence Mascara Lash Princess", "price": 9.99, "stock": 99},
    2: {"id": 2, "title": "Eyeshadow Palette with Mirror", "price": 19.99, "stock": 6},
    3: {"id": 3, "title": "Powder Canister", "price": 14.99, "stock": 10},
    4: {"id": 4, "title": "Red Lipstick", "price": 12.99, "stock": 0},
    5: {"id": 5, "title": "Red Nail Polish", "price": 8.99, "stock": 52},
}


class ProductService:
    def exists(self, product_id: int) -> bool:
        """EXAMPLE, already finished. Is there a product with this id?"""
        return product_id in PRODUCTS

    def _with_flags(self, product: dict) -> dict:
        """TASK 1: return a NEW dictionary with everything in `product`, plus "low_stock".

        "low_stock" must be True when the product's stock is below LOW_STOCK_LIMIT,
        and False otherwise. Do not change the dictionary that was passed in.
        """
        # The rule: stock below the limit means low stock.
        # The comparison already gives True or False.
        low_stock = product["stock"] < LOW_STOCK_LIMIT

        # `**product` copies every key of the product into a NEW dictionary,
        # and then we add one more key. The original is not changed.
        return {**product, "low_stock": low_stock}

    def get_by_id(self, product_id: int) -> dict | None:
        """TASK 2: return the product with this id, with the "low_stock" flag.

        If there is no product with this id, return None.
        Use self._with_flags(...) so that the rule is written in only one place.
        """
        # .get(...) gives None when the id is not in the dictionary.
        product = PRODUCTS.get(product_id)

        if product is None:
            return None

        # Reuse Task 1, so the rule lives in one place only.
        return self._with_flags(product)
