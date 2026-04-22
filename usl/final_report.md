# Final Report

## Objective

The goal of this project was to build a pharmacy analytics solution focused on sales analysis and expiry tracking. The final output helps monitor revenue patterns, category contribution, and batch-level stock that may expire before being sold.

## Scope

The project covers:

- pharmacy medicine master data
- inventory batch data with expiry dates
- sales transaction data
- summary analysis for business reporting
- executive dashboard creation

## Data Summary

- Medicines: `100`
- Inventory batches: `391`
- Sales transactions: `30,000`
- Sales date coverage: approximately one year

Main source files:

- [medicine_master.csv](C:/Users/pkunj/Documents/Codex/usl/data/pharmacy_30k/medicine_master.csv)
- [inventory_batches.csv](C:/Users/pkunj/Documents/Codex/usl/data/pharmacy_30k/inventory_batches.csv)
- [sales_transactions.csv](C:/Users/pkunj/Documents/Codex/usl/data/pharmacy_30k/sales_transactions.csv)

## KPI Summary

- Total sales: `47,923,135.51`
- Total transactions: `30,000`
- Total units sold: `134,772`
- High-risk expiry value excluding `90+ days`: `270,830.63`

## Sales Insights

Key findings from the sales summaries:

- `Gastro` is the highest-grossing category with sales of `7,478,690.15`
- `Pain Relief` leads on volume with `16,730` units sold
- `Vitamins` is also a strong contributor with sales above `5.39M`
- Monthly revenue rises steadily across the year, showing expanding commercial activity in the dataset

## Expiry Insights

Key findings from the expiry summaries:

- Expired batches still hold stock and represent preventable loss
- The `31-60 days` bucket shows the highest near-term expiry value at `120,608.15`
- The `0-30 days` bucket also needs attention with `53,166.86` at risk
- Several top-risk batches belong to the `Hormonal` category, suggesting tighter review is needed there

## Top Risk Examples

Examples from the top risk list:

- `MED029-B03` with risk value `86,640.48`
- `MED018-B05` with risk value `51,959.72`
- `MED059-B04` with risk value `40,962.00`

Reference:

- [top_expiry_risk_batches.csv](C:/Users/pkunj/Documents/Codex/usl/data/summary/top_expiry_risk_batches.csv)

## Dashboard Delivered

The final dashboard workbook includes:

- executive KPI cards
- monthly revenue trend
- category sales mix
- expiry bucket distribution
- top risk batches
- detailed supporting sheets for sales and expiry analysis

Dashboard file:

- [pharmacy-sales-expiry-dashboard.xlsx](C:/Users/pkunj/Documents/Codex/usl/outputs/pharmacy-dashboard/pharmacy-sales-expiry-dashboard.xlsx)

## Recommendations

1. Review `0-30 day` and `31-60 day` expiry buckets weekly.
2. Apply discounting or promotion strategies for high-risk near-expiry stock.
3. Strengthen FEFO inventory handling for categories showing repeated risk.
4. Reassess purchasing levels for slow-moving stock with high expiry exposure.
5. Use the dashboard as a recurring review tool for category sales and expiry control.

## Conclusion

This project successfully delivers a pharmacy analytics workflow from raw data generation to business-ready reporting. It gives a strong starting point for a real-world sales and expiry management solution and can be extended into forecasting, profit analysis, or Power BI deployment.
