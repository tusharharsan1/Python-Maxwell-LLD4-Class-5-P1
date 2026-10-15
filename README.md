# Low Stock Flag at ShopNest

> **Where the files are:** the starter files in the `base/` folder. Every path below (such as `app/services/product_service.py` and `try_it.py`) is inside `base/`. Open a terminal in `base/` to run the commands.

## Problem Statement
We want to show "Only a few left!" next to products that are almost sold out. The shop owner gave us one simple rule to decide this. We keep rules like this inside a service class (as we did in class), so that the rule lives in one place and is easy to test. Complete the `ProductService` so that it applies this rule to our products.

## Requirements
### Low stock rule
A product is **low stock** when its `stock` is **below** `LOW_STOCK_LIMIT`. At the moment the limit is 10.
- The limit is written once, as the name `LOW_STOCK_LIMIT`. The owner may change it one day, so the code must use the name and not the number 10.
- A stock that is exactly equal to the limit is **not** low stock.

| Stock | Low stock? |
|---|---|
| 0 | Yes |
| 3 | Yes |
| 9 | Yes |
| 10 | No |
| 52 | No |

### Products
A product is a plain dictionary with the keys `id`, `title`, `price` and `stock`. The products are kept in the `PRODUCTS` dictionary, in memory. This is our pretend database.

| id | title | stock | Low stock? |
|---|---|---|---|
| 1 | Essence Mascara Lash Princess | 99 | No |
| 2 | Eyeshadow Palette with Mirror | 6 | Yes |
| 3 | Powder Canister | 10 | No |
| 4 | Red Lipstick | 0 | Yes |
| 5 | Red Nail Polish | 52 | No |

### Adding the flag
When a product leaves the service, it must carry one extra key: `"low_stock"`, with the value `True` or `False`.
- The flag is added to a **copy** of the product. The dictionary that was passed in, and the products stored in `PRODUCTS`, must stay exactly as they were.

Example:
```python
{"id": 9, "title": "Pen", "price": 1.5, "stock": 3}
# becomes
{"id": 9, "title": "Pen", "price": 1.5, "stock": 3, "low_stock": True}
```

### Getting one product
Given a product id, the service returns that product **with** the `"low_stock"` flag.
- If there is no product with that id, the service returns `None`.
- Turning "not found" into an HTTP `404` is **not** the service's job. The router does that (as in class).

| Call | Result |
|---|---|
| `get_by_id(2)` | the Eyeshadow Palette, with `"low_stock": True` |
| `get_by_id(1)` | the Essence Mascara, with `"low_stock": False` |
| `get_by_id(99)` | `None` |

To achieve these requirements we need to do 2 things:
- Complete `_with_flags`, which builds the copy of a product with the `low_stock` flag.
- Complete `get_by_id`, which finds a product and returns it with the flag, or `None`.

## Instructions
1. We need to implement `_with_flags` inside the `ProductService` class in `app/services/product_service.py`.
2. We need to implement `get_by_id` inside the same class. Use `_with_flags` inside it, so that the rule is written in only one place.
3. Do not modify the existing method `exists`, the `PRODUCTS` dictionary, or the names and parameters of the methods. Feel free to add new methods if required.
4. Do not write the number 10 in your code. Use `LOW_STOCK_LIMIT`.
5. Do not add keys to the dictionaries inside `PRODUCTS`. Return a copy.
6. When a method is finished, delete the `raise NotImplementedError(...)` line inside it.
7. Run `python try_it.py` from this folder (the one that contains `app/` and `try_it.py`) to see what your code does. When both methods are finished, you should see exactly this:
   ```
   Task 1: _with_flags
     low stock product : {'id': 9, 'title': 'Pen', 'price': 1.5, 'stock': 3, 'low_stock': True}
     original unchanged: {'id': 9, 'title': 'Pen', 'price': 1.5, 'stock': 3}
     stock exactly 10  : False
   Task 2: get_by_id
     id 2 : {'id': 2, 'title': 'Eyeshadow Palette with Mirror', 'price': 19.99, 'stock': 6, 'low_stock': True}
     id 1 : {'id': 1, 'title': 'Essence Mascara Lash Princess', 'price': 9.99, 'stock': 99, 'low_stock': False}
     id 99: None
     PRODUCTS[2] has no low_stock key: True
   ```
   If you see `not done yet`, one of the methods still has its `raise` line.
8. Your code will be checked with the test file `tests/test_product_service.py`. It checks the cases in the Requirements above, and the rules in instructions 3, 4 and 5. While you write your code, use `python try_it.py` (instruction 7) to check your work.
9. We will be using an in-memory dictionary for this assignment. You do not need FastAPI, a server, or any package to install.
10. Hints (all of these were in class):
    - **Copy a dictionary and add a key.** A `**` in front of a dictionary spreads it into a new dictionary:
      ```python
      point = {"x": 1, "y": 2}
      bigger = {**point, "z": 3}
      # bigger is {"x": 1, "y": 2, "z": 3}, and point is unchanged
      ```
    - **Look up a key without an error.** `.get(...)` gives `None` when the key is missing:
      ```python
      colours = {1: "red", 2: "blue"}
      colours.get(2)   # "blue"
      colours.get(7)   # None
      ```
    - **A comparison already is `True` or `False`.** For example `3 < 10` is `True`.
