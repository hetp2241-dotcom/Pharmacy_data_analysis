from __future__ import annotations

import csv
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


SEED = 20260422
BASE_DATE = date(2026, 4, 22)
SALES_RECORD_TARGET = 30000
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "pharmacy_30k"

CATEGORIES = [
    "Pain Relief",
    "Antibiotic",
    "Diabetes",
    "Cardiac",
    "Gastro",
    "Allergy",
    "Vitamins",
    "Respiratory",
    "Hormonal",
    "Neurology",
]

DOSAGE_FORMS = ["Tablet", "Capsule", "Syrup", "Injection", "Inhaler"]
STRENGTHS = ["5 mg", "10 mg", "20 mg", "50 mg", "100 mg", "250 mg", "500 mg", "100 ml"]
BRANDS = ["MediCure", "Healix", "NovaMed", "LifeDrop", "PulseRx", "Digesta", "Airleaf", "NutriZen"]
MANUFACTURERS = [
    "Sunwell Pharma",
    "ZenBio Labs",
    "Apex Remedies",
    "Metro Health",
    "Careline Drugs",
    "PrimeCrest",
    "Wellspring Labs",
    "NorthStar Pharma",
]
SUPPLIERS = [
    "Apex Wholesale",
    "CareHub Distributors",
    "Prime MedSupply",
    "Urban Pharma Chain",
    "Wellroute Healthcare",
    "MediBridge Supply",
]
PAYMENT_MODES = ["Cash", "Card", "UPI"]

MEDICINE_NAME_PARTS_A = [
    "Para", "Ibu", "Cefi", "Amo", "Azi", "Glu", "Card", "Ome", "Panto", "Ceti",
    "Mont", "Vita", "B12", "Cough", "Bron", "Zin", "Thyro", "Neuro", "Cal", "Lev",
]
MEDICINE_NAME_PARTS_B = [
    "cure", "fast", "med", "plus", "safe", "nil", "zen", "max", "care", "rid",
    "tide", "rise", "air", "well", "vita", "sure", "calm", "boost", "aid", "flow",
]
GENERIC_NAMES = [
    "Paracetamol", "Ibuprofen", "Cefixime", "Amoxicillin", "Azithromycin", "Metformin",
    "Insulin Glargine", "Atorvastatin", "Amlodipine", "Omeprazole", "Pantoprazole",
    "Cetirizine", "Montelukast", "Multivitamin", "Methylcobalamin", "Dextromethorphan",
    "Salbutamol", "Levothyroxine", "Pregabalin", "Calcium Carbonate",
]


@dataclass(frozen=True)
class Medicine:
    medicine_id: str
    medicine_name: str
    category: str
    brand: str
    generic_name: str
    manufacturer: str
    dosage_form: str
    strength: str
    unit_price: float
    cost_price: float


def build_medicines(total: int = 100) -> list[Medicine]:
    random.seed(SEED)
    medicines: list[Medicine] = []

    for index in range(total):
        category = CATEGORIES[index % len(CATEGORIES)]
        brand = BRANDS[index % len(BRANDS)]
        manufacturer = MANUFACTURERS[index % len(MANUFACTURERS)]
        generic_name = GENERIC_NAMES[index % len(GENERIC_NAMES)]
        dosage_form = DOSAGE_FORMS[index % len(DOSAGE_FORMS)]
        strength = STRENGTHS[index % len(STRENGTHS)]
        name = f"{MEDICINE_NAME_PARTS_A[index % len(MEDICINE_NAME_PARTS_A)]}{MEDICINE_NAME_PARTS_B[(index * 3) % len(MEDICINE_NAME_PARTS_B)]} {index + 1}"
        cost_price = round(random.uniform(8, 420), 2)
        markup = random.uniform(1.35, 2.1)
        unit_price = round(cost_price * markup, 2)
        medicines.append(
            Medicine(
                medicine_id=f"MED{index + 1:03d}",
                medicine_name=name,
                category=category,
                brand=brand,
                generic_name=generic_name,
                manufacturer=manufacturer,
                dosage_form=dosage_form,
                strength=strength,
                unit_price=unit_price,
                cost_price=cost_price,
            )
        )

    return medicines


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_inventory(medicines: list[Medicine]) -> list[dict]:
    random.seed(SEED + 1)
    inventory_rows: list[dict] = []

    for medicine in medicines:
        batch_total = random.randint(3, 5)
        for batch_number in range(1, batch_total + 1):
            purchase_days_ago = random.randint(10, 420)
            purchase_date = BASE_DATE - timedelta(days=purchase_days_ago)
            shelf_life_days = random.randint(150, 720)
            expiry_date = purchase_date + timedelta(days=shelf_life_days)
            opening_stock = random.randint(180, 900)
            inventory_rows.append(
                {
                    "batch_no": f"{medicine.medicine_id}-B{batch_number:02d}",
                    "medicine_id": medicine.medicine_id,
                    "purchase_date": purchase_date.isoformat(),
                    "expiry_date": expiry_date.isoformat(),
                    "opening_stock": opening_stock,
                    "stock_in_hand": opening_stock,
                    "unit_cost": f"{medicine.cost_price:.2f}",
                    "supplier_name": random.choice(SUPPLIERS),
                    "inventory_value": f"{opening_stock * medicine.cost_price:.2f}",
                }
            )

    inventory_rows.sort(key=lambda row: (row["medicine_id"], row["expiry_date"], row["batch_no"]))
    return inventory_rows


def weighted_medicine_pool(medicines: list[Medicine]) -> list[Medicine]:
    category_weights = {
        "Pain Relief": 1.35,
        "Antibiotic": 1.25,
        "Diabetes": 1.10,
        "Cardiac": 1.00,
        "Gastro": 1.15,
        "Allergy": 0.95,
        "Vitamins": 1.20,
        "Respiratory": 0.90,
        "Hormonal": 0.75,
        "Neurology": 0.70,
    }
    pool: list[Medicine] = []
    for medicine in medicines:
        repeats = max(1, int(category_weights[medicine.category] * 10))
        pool.extend([medicine] * repeats)
    return pool


def choose_batch(inventory_by_medicine: dict[str, list[dict]], medicine_id: str, sale_date: date) -> dict | None:
    eligible = []
    for batch in inventory_by_medicine[medicine_id]:
        purchase_date = date.fromisoformat(batch["purchase_date"])
        expiry_date = date.fromisoformat(batch["expiry_date"])
        if purchase_date <= sale_date <= expiry_date and batch["stock_in_hand"] > 0:
            eligible.append(batch)

    if not eligible:
        return None

    eligible.sort(key=lambda batch: batch["expiry_date"])
    return eligible[0]


def generate_sales(medicines: list[Medicine], inventory_rows: list[dict]) -> list[dict]:
    random.seed(SEED + 2)
    medicine_lookup = {medicine.medicine_id: medicine for medicine in medicines}
    inventory_by_medicine: dict[str, list[dict]] = defaultdict(list)
    for batch in inventory_rows:
        inventory_by_medicine[batch["medicine_id"]].append(batch)

    pool = weighted_medicine_pool(medicines)
    sales_rows: list[dict] = []
    start_date = BASE_DATE - timedelta(days=364)

    while len(sales_rows) < SALES_RECORD_TARGET:
        medicine = random.choice(pool)
        sale_date = start_date + timedelta(days=random.randint(0, 364))
        batch = choose_batch(inventory_by_medicine, medicine.medicine_id, sale_date)
        if batch is None:
            continue

        quantity = min(random.randint(1, 8), int(batch["stock_in_hand"]))
        if quantity <= 0:
            continue

        sale_unit_price = round(medicine.unit_price * random.uniform(0.94, 1.08), 2)
        discount_pct = random.choice([0, 0, 0, 5, 10, 12])
        gross_amount = quantity * sale_unit_price
        net_amount = round(gross_amount * (1 - discount_pct / 100), 2)

        batch["stock_in_hand"] -= quantity
        batch["inventory_value"] = f"{float(batch['unit_cost']) * batch['stock_in_hand']:.2f}"

        sales_rows.append(
            {
                "sale_id": f"SALE{len(sales_rows) + 1:06d}",
                "sale_date": sale_date.isoformat(),
                "medicine_id": medicine.medicine_id,
                "batch_no": batch["batch_no"],
                "quantity_sold": quantity,
                "unit_price": f"{sale_unit_price:.2f}",
                "discount_pct": discount_pct,
                "total_amount": f"{net_amount:.2f}",
                "payment_mode": random.choice(PAYMENT_MODES),
            }
        )

    sales_rows.sort(key=lambda row: (row["sale_date"], row["sale_id"]))
    return sales_rows


def medicine_rows(medicines: list[Medicine]) -> list[dict]:
    rows: list[dict] = []
    for medicine in medicines:
        rows.append(
            {
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "category": medicine.category,
                "brand": medicine.brand,
                "generic_name": medicine.generic_name,
                "manufacturer": medicine.manufacturer,
                "dosage_form": medicine.dosage_form,
                "strength": medicine.strength,
                "unit_price": f"{medicine.unit_price:.2f}",
                "cost_price": f"{medicine.cost_price:.2f}",
                "profit_margin_pct": f"{((medicine.unit_price - medicine.cost_price) / medicine.unit_price) * 100:.2f}",
            }
        )
    return rows


def main() -> None:
    medicines = build_medicines()
    inventory_rows = generate_inventory(medicines)
    sales_rows = generate_sales(medicines, inventory_rows)

    write_csv(
        OUTPUT_DIR / "medicine_master.csv",
        [
            "medicine_id",
            "medicine_name",
            "category",
            "brand",
            "generic_name",
            "manufacturer",
            "dosage_form",
            "strength",
            "unit_price",
            "cost_price",
            "profit_margin_pct",
        ],
        medicine_rows(medicines),
    )
    write_csv(
        OUTPUT_DIR / "inventory_batches.csv",
        [
            "batch_no",
            "medicine_id",
            "purchase_date",
            "expiry_date",
            "opening_stock",
            "stock_in_hand",
            "unit_cost",
            "supplier_name",
            "inventory_value",
        ],
        inventory_rows,
    )
    write_csv(
        OUTPUT_DIR / "sales_transactions.csv",
        [
            "sale_id",
            "sale_date",
            "medicine_id",
            "batch_no",
            "quantity_sold",
            "unit_price",
            "discount_pct",
            "total_amount",
            "payment_mode",
        ],
        sales_rows,
    )

    print(f"Created {len(medicines)} medicine records")
    print(f"Created {len(inventory_rows)} inventory batch records")
    print(f"Created {len(sales_rows)} sales transaction records")


if __name__ == "__main__":
    main()
