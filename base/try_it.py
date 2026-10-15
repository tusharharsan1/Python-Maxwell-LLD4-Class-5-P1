"""Run this file to see what your code does:   python try_it.py

You do not need to change anything in this file.
"""
from app.services.product_service import PRODUCTS, ProductService

service = ProductService()

print("Task 1: _with_flags")
try:
    pen = {"id": 9, "title": "Pen", "price": 1.5, "stock": 3}
    print("  low stock product :", service._with_flags(pen))
    print("  original unchanged:", pen)
    ten = {"id": 9, "title": "Pen", "price": 1.5, "stock": 10}
    print("  stock exactly 10  :", service._with_flags(ten)["low_stock"])
except NotImplementedError as error:
    print("  not done yet ->", error)

print("Task 2: get_by_id")
try:
    print("  id 2 :", service.get_by_id(2))
    print("  id 1 :", service.get_by_id(1))
    print("  id 99:", service.get_by_id(99))
    print("  PRODUCTS[2] has no low_stock key:", "low_stock" not in PRODUCTS[2])
except NotImplementedError as error:
    print("  not done yet ->", error)
