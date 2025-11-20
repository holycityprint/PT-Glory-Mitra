import os
from flask import Blueprint

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "hrd")

print("=== HRD template folder ===")
print(TEMPLATE_DIR)

# Blueprint utama HRD
hrd_bp = Blueprint(
    "hrd",
    __name__,
    url_prefix="/hrd",
    template_folder=TEMPLATE_DIR
)

# Impor semua modul HRD (dashboard, employee, performance)
from . import dashboard, employee, performance

__all__ = ["hrd_bp"]