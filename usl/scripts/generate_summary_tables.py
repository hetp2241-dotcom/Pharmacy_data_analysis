from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "pharmacy_30k"
OUTPUT_DIR = BASE_DIR / "data" / "summary"
AS_OF_DATE = date(2026, 4, 22)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_float(value: str) -> float:
    return float(value) if value not in (None, "") else 0.0


def safe_int(value: str) -> int:
    return int(float(value)) if value not in (None, "") else 0


def build_lookups(medicines: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    medicine_by_id = {row["medicine_id"]: row for row in medicines}
    category_by_id = {row["medicine_id"]: row["category"] for row in medicines}
    return medicine_by_id, category_by_id


def monthly_sales_summary(sales: list[dict[str, str]]) -> list[dict]:
    summary: dict[str, dict[str, float]] = defaultdict(lambda: {
        "transaction_count": 0,
        "quantity_sold": 0,
        "gross_sales": 0.0,
    })

    for row in sales:
        month_key = row["sale_date"][:7]
        summary[month_key]["transaction_count"] += 1
        summary[month_key]["quantity_sold"] += safe_int(row["quantity_sold"])
        summary[month_key]["gross_sales"] += safe_float(row["total_amount"])

    rows = []
    for month_key in sorted(summary):
        rows.append(
            {
                "month": month_key,
                "transaction_count": int(summary[month_key]["transaction_count"]),
                "quantity_sold": int(summary[month_key]["quantity_sold"]),
                "gross_sales": f"{summary[month_key]['gross_sales']:.2f}",
            }
        )
    return rows


def medicine_sales_summary(sales: list[dict[str, str]], medicine_by_id: dict[str, dict[str, str]]) -> list[dict]:
    summary: dict[str, dict[str, float]] = defaultdict(lambda: {
        "transaction_count": 0,
        "quantity_sold": 0,
        "gross_sales": 0.0,
    })

    for row in sales:
        medicine_id = row["medicine_id"]
        summary[medicine_id]["transaction_count"] += 1
        summary[medicine_id]["quantity_sold"] += safe_int(row["quantity_sold"])
        summary[medicine_id]["gross_sales"] += safe_float(row["total_amount"])

    rows = []
    for medicine_id, metrics in summary.items():
        medicine = medicine_by_id[medicine_id]
        rows.append(
            {
                "medicine_id": medicine_id,
                "medicine_name": medicine["medicine_name"],
                "category": medicine["category"],
                "brand": medicine["brand"],
                "transaction_count": int(metrics["transaction_count"]),
                "quantity_sold": int(metrics["quantity_sold"]),
                "gross_sales": f"{metrics['gross_sales']:.2f}",
                "average_sale_value": f"{(metrics['gross_sales'] / metrics['transaction_count']):.2f}",
            }
        )

    rows.sort(key=lambda row: float(row["gross_sales"]), reverse=True)
    return rows


def category_sales_summary(sales: list[dict[str, str]], category_by_id: dict[str, str]) -> list[dict]:
    summary: dict[str, dict[str, float]] = defaultdict(lambda: {
        "transaction_count": 0,
        "quantity_sold": 0,
        "gross_sales": 0.0,
    })

    for row in sales:
        category = category_by_id[row["medicine_id"]]
        summary[category]["transaction_count"] += 1
        summary[category]["quantity_sold"] += safe_int(row["quantity_sold"])
        summary[category]["gross_sales"] += safe_float(row["total_amount"])

    rows = []
    for category, metrics in summary.items():
        rows.append(
            {
                "category": category,
                "transaction_count": int(metrics["transaction_count"]),
                "quantity_sold": int(metrics["quantity_sold"]),
                "gross_sales": f"{metrics['gross_sales']:.2f}",
            }
        )

    rows.sort(key=lambda row: float(row["gross_sales"]), reverse=True)
    return rows


def sales_velocity_summary(
    sales: list[dict[str, str]],
    medicine_by_id: dict[str, dict[str, str]],
) -> dict[str, dict[str, float]]:
    velocity: dict[str, dict[str, float]] = defaultdict(lambda: {
        "total_quantity_sold": 0,
        "transaction_count": 0,
    })

    for row in sales:
        medicine_id = row["medicine_id"]
        velocity[medicine_id]["total_quantity_sold"] += safe_int(row["quantity_sold"])
        velocity[medicine_id]["transaction_count"] += 1

    for medicine_id in medicine_by_id:
        avg_daily_units = velocity[medicine_id]["total_quantity_sold"] / 365
        velocity[medicine_id]["avg_daily_units"] = round(avg_daily_units, 2)

    return velocity


def classify_expiry_bucket(days_to_expiry: int) -> str:
    if days_to_expiry < 0:
        return "Expired"
    if days_to_expiry <= 30:
        return "0-30 days"
    if days_to_expiry <= 60:
        return "31-60 days"
    if days_to_expiry <= 90:
        return "61-90 days"
    return "90+ days"


def expiry_detail_summary(
    inventory: list[dict[str, str]],
    medicine_by_id: dict[str, dict[str, str]],
    velocity_by_id: dict[str, dict[str, float]],
) -> list[dict]:
    rows = []

    for row in inventory:
        medicine = medicine_by_id[row["medicine_id"]]
        expiry_date = date.fromisoformat(row["expiry_date"])
        days_to_expiry = (expiry_date - AS_OF_DATE).days
        stock_in_hand = safe_int(row["stock_in_hand"])
        avg_daily_units = velocity_by_id[row["medicine_id"]]["avg_daily_units"]
        projected_units_before_expiry = round(max(days_to_expiry, 0) * avg_daily_units, 2)
        at_risk_units = max(0, round(stock_in_hand - projected_units_before_expiry, 2))
        expiry_risk_value = at_risk_units * safe_float(row["unit_cost"])

        rows.append(
            {
                "batch_no": row["batch_no"],
                "medicine_id": row["medicine_id"],
                "medicine_name": medicine["medicine_name"],
                "category": medicine["category"],
                "supplier_name": row["supplier_name"],
                "purchase_date": row["purchase_date"],
                "expiry_date": row["expiry_date"],
                "days_to_expiry": days_to_expiry,
                "expiry_bucket": classify_expiry_bucket(days_to_expiry),
                "stock_in_hand": stock_in_hand,
                "avg_daily_units_sold": f"{avg_daily_units:.2f}",
                "projected_units_before_expiry": f"{projected_units_before_expiry:.2f}",
                "estimated_units_at_risk": f"{at_risk_units:.2f}",
                "estimated_expiry_risk_value": f"{expiry_risk_value:.2f}",
            }
        )

    rows.sort(
        key=lambda row: (
            {"Expired": 0, "0-30 days": 1, "31-60 days": 2, "61-90 days": 3, "90+ days": 4}[row["expiry_bucket"]],
            -float(row["estimated_expiry_risk_value"]),
        )
    )
    return rows


def expiry_bucket_summary(expiry_rows: list[dict]) -> list[dict]:
    summary: dict[str, dict[str, float]] = defaultdict(lambda: {
        "batch_count": 0,
        "stock_in_hand": 0,
        "estimated_expiry_risk_value": 0.0,
    })

    for row in expiry_rows:
        bucket = row["expiry_bucket"]
        summary[bucket]["batch_count"] += 1
        summary[bucket]["stock_in_hand"] += safe_int(str(row["stock_in_hand"]))
        summary[bucket]["estimated_expiry_risk_value"] += safe_float(row["estimated_expiry_risk_value"])

    ordered_buckets = ["Expired", "0-30 days", "31-60 days", "61-90 days", "90+ days"]
    rows = []
    for bucket in ordered_buckets:
        if bucket not in summary:
            continue
        rows.append(
            {
                "expiry_bucket": bucket,
                "batch_count": int(summary[bucket]["batch_count"]),
                "stock_in_hand": int(summary[bucket]["stock_in_hand"]),
                "estimated_expiry_risk_value": f"{summary[bucket]['estimated_expiry_risk_value']:.2f}",
            }
        )
    return rows


def top_expiry_risk_rows(expiry_rows: list[dict], limit: int = 25) -> list[dict]:
    active_risk_rows = [row for row in expiry_rows if row["expiry_bucket"] != "90+ days"]
    active_risk_rows.sort(key=lambda row: float(row["estimated_expiry_risk_value"]), reverse=True)
    return active_risk_rows[:limit]


def main() -> None:
    medicines = read_csv(INPUT_DIR / "medicine_master.csv")
    inventory = read_csv(INPUT_DIR / "inventory_batches.csv")
    sales = read_csv(INPUT_DIR / "sales_transactions.csv")

    medicine_by_id, category_by_id = build_lookups(medicines)
    velocity_by_id = sales_velocity_summary(sales, medicine_by_id)

    monthly_rows = monthly_sales_summary(sales)
    medicine_rows = medicine_sales_summary(sales, medicine_by_id)
    category_rows = category_sales_summary(sales, category_by_id)
    expiry_rows = expiry_detail_summary(inventory, medicine_by_id, velocity_by_id)
    expiry_bucket_rows = expiry_bucket_summary(expiry_rows)
    top_risk_rows = top_expiry_risk_rows(expiry_rows)

    write_csv(
        OUTPUT_DIR / "monthly_sales_summary.csv",
        ["month", "transaction_count", "quantity_sold", "gross_sales"],
        monthly_rows,
    )
    write_csv(
        OUTPUT_DIR / "medicine_sales_summary.csv",
        [
            "medicine_id",
            "medicine_name",
            "category",
            "brand",
            "transaction_count",
            "quantity_sold",
            "gross_sales",
            "average_sale_value",
        ],
        medicine_rows,
    )
    write_csv(
        OUTPUT_DIR / "category_sales_summary.csv",
        ["category", "transaction_count", "quantity_sold", "gross_sales"],
        category_rows,
    )
    write_csv(
        OUTPUT_DIR / "expiry_batch_detail.csv",
        [
            "batch_no",
            "medicine_id",
            "medicine_name",
            "category",
            "supplier_name",
            "purchase_date",
            "expiry_date",
            "days_to_expiry",
            "expiry_bucket",
            "stock_in_hand",
            "avg_daily_units_sold",
            "projected_units_before_expiry",
            "estimated_units_at_risk",
            "estimated_expiry_risk_value",
        ],
        expiry_rows,
    )
    write_csv(
        OUTPUT_DIR / "expiry_bucket_summary.csv",
        ["expiry_bucket", "batch_count", "stock_in_hand", "estimated_expiry_risk_value"],
        expiry_bucket_rows,
    )
    write_csv(
        OUTPUT_DIR / "top_expiry_risk_batches.csv",
        [
            "batch_no",
            "medicine_id",
            "medicine_name",
            "category",
            "supplier_name",
            "purchase_date",
            "expiry_date",
            "days_to_expiry",
            "expiry_bucket",
            "stock_in_hand",
            "avg_daily_units_sold",
            "projected_units_before_expiry",
            "estimated_units_at_risk",
            "estimated_expiry_risk_value",
        ],
        top_risk_rows,
    )

    print(f"Created {len(monthly_rows)} monthly summary rows")
    print(f"Created {len(medicine_rows)} medicine summary rows")
    print(f"Created {len(category_rows)} category summary rows")
    print(f"Created {len(expiry_rows)} expiry detail rows")
    print(f"Created {len(top_risk_rows)} top expiry risk rows")


if __name__ == "__main__":
    main()
