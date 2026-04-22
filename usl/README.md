# Pharmacy Sales Analysis and Expiry Tracking

This project analyzes pharmacy sales performance and expiry risk using a generated retail pharmacy dataset. It combines raw transactional data, summary tables, and a presentation-ready dashboard to help a pharmacy owner or operations team make better stock, pricing, and expiry decisions.

## Project Goal

The project focuses on two business problems:

- understanding medicine sales performance
- identifying stock and batch expiry risk before loss happens

## Project Outputs

- Large linked dataset with `30,000` sales transactions
- Summary tables for sales, category performance, and expiry risk
- Excel dashboard for executive review
- Scripts to regenerate the dataset, summaries, and dashboard

## Tools Used

- Python
- Excel dashboard output
- CSV files for raw and summary data
- JavaScript workbook builder for dashboard generation

## Folder Structure

```text
usl/
  data/
    pharmacy_30k/
    summary/
  outputs/
    pharmacy-dashboard/
  scripts/
  README.md
  final_report.md
  project_summary.md
```

## Main Data Files

Raw data:

- [medicine_master.csv](C:/Users/pkunj/Documents/Codex/usl/data/pharmacy_30k/medicine_master.csv)
- [inventory_batches.csv](C:/Users/pkunj/Documents/Codex/usl/data/pharmacy_30k/inventory_batches.csv)
- [sales_transactions.csv](C:/Users/pkunj/Documents/Codex/usl/data/pharmacy_30k/sales_transactions.csv)

Summary data:

- [monthly_sales_summary.csv](C:/Users/pkunj/Documents/Codex/usl/data/summary/monthly_sales_summary.csv)
- [category_sales_summary.csv](C:/Users/pkunj/Documents/Codex/usl/data/summary/category_sales_summary.csv)
- [medicine_sales_summary.csv](C:/Users/pkunj/Documents/Codex/usl/data/summary/medicine_sales_summary.csv)
- [expiry_bucket_summary.csv](C:/Users/pkunj/Documents/Codex/usl/data/summary/expiry_bucket_summary.csv)
- [top_expiry_risk_batches.csv](C:/Users/pkunj/Documents/Codex/usl/data/summary/top_expiry_risk_batches.csv)

Dashboard:

- [pharmacy-sales-expiry-dashboard.xlsx](C:/Users/pkunj/Documents/Codex/usl/outputs/pharmacy-dashboard/pharmacy-sales-expiry-dashboard.xlsx)

## Dataset Overview

The dataset includes:

- `100` medicines
- `391` inventory batches
- `30,000` sales transactions

Core business tables:

- `medicine_master`: product attributes, category, brand, pricing
- `inventory_batches`: purchase date, expiry date, opening stock, current stock
- `sales_transactions`: transaction-level sales with medicine and batch references

## Business Questions Answered

- Which categories drive the most sales?
- Which medicines perform best?
- Which stock batches are close to expiry?
- How much inventory value is at expiry risk?
- Which products need review for discounting, clearance, or stricter inventory control?

## Workflow

1. Generate the pharmacy dataset with [generate_pharmacy_dataset.py](C:/Users/pkunj/Documents/Codex/usl/scripts/generate_pharmacy_dataset.py)
2. Build analysis summaries with [generate_summary_tables.py](C:/Users/pkunj/Documents/Codex/usl/scripts/generate_summary_tables.py)
3. Create the final dashboard with [build_pharmacy_dashboard.mjs](C:/Users/pkunj/Documents/Codex/usl/scripts/build_pharmacy_dashboard.mjs)

## Key Results

- Total sales: about `47.92M`
- Total transactions: `30,000`
- Total units sold: `134,772`
- Expiry risk value outside the `90+ days` bucket: about `270,830.63`
- Top sales category: `Gastro`

## Business Value

This project gives a pharmacy team a simple analytics setup to:

- monitor category and product sales
- identify slow-moving and risky stock
- review near-expiry batches early
- improve reorder and clearance decisions

## Next Improvements

- Add profit analysis using cost and selling price at transaction level
- Add supplier performance tracking
- Add reorder alerts and sales forecasting
- Publish the dashboard in Power BI for interactive filtering
