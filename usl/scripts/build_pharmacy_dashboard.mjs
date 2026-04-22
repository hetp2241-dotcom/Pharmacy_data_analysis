import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");
const summaryDir = path.join(rootDir, "data", "summary");
const outputDir = path.join(rootDir, "outputs", "pharmacy-dashboard");
const outputPath = path.join(outputDir, "pharmacy-sales-expiry-dashboard.xlsx");
const previewPath = path.join(outputDir, "dashboard-preview.png");

const theme = {
  ink: "#0F172A",
  slate: "#475569",
  blue: "#0F4C81",
  sky: "#77B6EA",
  mint: "#39A78E",
  gold: "#E2A93B",
  coral: "#E76F51",
  cream: "#F8F5EF",
  line: "#D7DEE8",
  panel: "#FFFFFF",
};

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

async function loadCsv(filename) {
  const text = await fs.readFile(path.join(summaryDir, filename), "utf8");
  return parseCsv(text);
}

function formatMoney(value) {
  return Number(value).toFixed(2);
}

function formatInteger(value) {
  return Math.round(Number(value));
}

function setRangeValues(sheet, startCell, rows) {
  sheet.getRange(startCell).write(rows);
}

function applySectionTitle(sheet, cell, text, endCell) {
  const range = sheet.getRange(`${cell}:${endCell}`);
  range.merge();
  range.values = [[text]];
  range.format = {
    fill: theme.blue,
    font: { color: "#FFFFFF", bold: true, size: 14 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
}

function styleTable(sheet, rangeAddress, headerRangeAddress) {
  sheet.getRange(headerRangeAddress).format = {
    fill: theme.ink,
    font: { color: "#FFFFFF", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  sheet.getRange(rangeAddress).format = {
    fill: "#FFFFFF",
    font: { color: theme.ink, size: 10 },
    borders: { item: { style: "Continuous", color: theme.line } },
  };
}

async function main() {
  const monthly = await loadCsv("monthly_sales_summary.csv");
  const category = await loadCsv("category_sales_summary.csv");
  const medicine = await loadCsv("medicine_sales_summary.csv");
  const expiryBuckets = await loadCsv("expiry_bucket_summary.csv");
  const topRisk = await loadCsv("top_expiry_risk_batches.csv");

  const workbook = Workbook.create();
  const dashboard = workbook.worksheets.add("Dashboard");
  const salesSheet = workbook.worksheets.add("Sales Summary");
  const expirySheet = workbook.worksheets.add("Expiry Summary");
  const productSheet = workbook.worksheets.add("Product Detail");

  [dashboard, salesSheet, expirySheet, productSheet].forEach((sheet) => {
    sheet.showGridLines = false;
  });

  dashboard.getRange("A1:P28").format.fill = theme.cream;
  dashboard.getRange("A1:P28").format.font = { color: theme.ink, name: "Aptos" };

  dashboard.getRange("A1:P2").merge();
  dashboard.getRange("A1").values = [["Pharmacy Sales and Expiry Dashboard"]];
  dashboard.getRange("A1").format = {
    fill: theme.ink,
    font: { color: "#FFFFFF", bold: true, size: 22 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };

  dashboard.getRange("A3:P3").merge();
  dashboard.getRange("A3").values = [["Built from the 30,000-transaction pharmacy dataset | Focus: revenue flow, category mix, and expiry risk exposure"]];
  dashboard.getRange("A3").format = {
    fill: theme.blue,
    font: { color: "#FFFFFF", size: 11 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };

  const totalSales = monthly.reduce((sum, row) => sum + Number(row.gross_sales), 0);
  const totalTransactions = monthly.reduce((sum, row) => sum + Number(row.transaction_count), 0);
  const totalUnits = monthly.reduce((sum, row) => sum + Number(row.quantity_sold), 0);
  const highRiskValue = expiryBuckets
    .filter((row) => row.expiry_bucket !== "90+ days")
    .reduce((sum, row) => sum + Number(row.estimated_expiry_risk_value), 0);

  const kpis = [
    ["Total Sales", totalSales, theme.blue, "$#,##0"],
    ["Transactions", totalTransactions, theme.mint, "#,##0"],
    ["Units Sold", totalUnits, theme.gold, "#,##0"],
    ["Expiry Risk Value", highRiskValue, theme.coral, "$#,##0"],
  ];

  const cardRanges = ["A5:D8", "E5:H8", "I5:L8", "M5:P8"];
  kpis.forEach(([label, value, color, format], index) => {
    const range = dashboard.getRange(cardRanges[index]);
    range.format = { fill: color, font: { color: "#FFFFFF" } };
    range.getCell(0, 0).values = [[label]];
    range.getCell(0, 0).format = { font: { bold: true, size: 11, color: "#FFFFFF" } };
    range.getCell(2, 0).values = [[Number(value)]];
    range.getCell(2, 0).format = {
      font: { bold: true, size: 18, color: "#FFFFFF" },
      numberFormat: format,
    };
    range.getRange("A1:D4").format.wrapText = false;
  });
  dashboard.getRange("A5:P8").format.rowHeightPx = 24;

  applySectionTitle(dashboard, "A10", "Monthly Revenue Trend", "G10");
  applySectionTitle(dashboard, "I10", "Category Sales Mix", "P10");
  applySectionTitle(dashboard, "A20", "Expiry Exposure", "G20");
  applySectionTitle(dashboard, "I20", "Top Risk Batches", "P20");

  const monthlyMatrix = [
    ["Month", "Transactions", "Units Sold", "Gross Sales"],
    ...monthly.map((row) => [
      row.month,
      Number(row.transaction_count),
      Number(row.quantity_sold),
      Number(row.gross_sales),
    ]),
  ];
  setRangeValues(salesSheet, "A1", monthlyMatrix);
  styleTable(salesSheet, `A1:D${monthlyMatrix.length}`, "A1:D1");
  salesSheet.getRange(`D2:D${monthlyMatrix.length}`).format.numberFormat = "$#,##0.00";

  const categoryMatrix = [
    ["Category", "Transactions", "Units Sold", "Gross Sales"],
    ...category.map((row) => [
      row.category,
      Number(row.transaction_count),
      Number(row.quantity_sold),
      Number(row.gross_sales),
    ]),
  ];
  setRangeValues(salesSheet, "F1", categoryMatrix);
  styleTable(salesSheet, `F1:I${categoryMatrix.length}`, "F1:I1");
  salesSheet.getRange(`I2:I${categoryMatrix.length}`).format.numberFormat = "$#,##0.00";

  const medicineTop20 = medicine.slice(0, 20);
  const medicineMatrix = [
    ["Medicine ID", "Medicine Name", "Category", "Brand", "Transactions", "Units Sold", "Gross Sales", "Average Sale Value"],
    ...medicineTop20.map((row) => [
      row.medicine_id,
      row.medicine_name,
      row.category,
      row.brand,
      Number(row.transaction_count),
      Number(row.quantity_sold),
      Number(row.gross_sales),
      Number(row.average_sale_value),
    ]),
  ];
  setRangeValues(productSheet, "A1", medicineMatrix);
  styleTable(productSheet, `A1:H${medicineMatrix.length}`, "A1:H1");
  productSheet.getRange(`G2:H${medicineMatrix.length}`).format.numberFormat = "$#,##0.00";

  const expiryBucketMatrix = [
    ["Expiry Bucket", "Batch Count", "Stock In Hand", "Risk Value"],
    ...expiryBuckets.map((row) => [
      row.expiry_bucket,
      Number(row.batch_count),
      Number(row.stock_in_hand),
      Number(row.estimated_expiry_risk_value),
    ]),
  ];
  setRangeValues(expirySheet, "A1", expiryBucketMatrix);
  styleTable(expirySheet, `A1:D${expiryBucketMatrix.length}`, "A1:D1");
  expirySheet.getRange(`D2:D${expiryBucketMatrix.length}`).format.numberFormat = "$#,##0.00";

  const topRiskMatrix = [
    ["Batch No", "Medicine", "Category", "Expiry Bucket", "Days To Expiry", "Stock", "Risk Value"],
    ...topRisk.slice(0, 15).map((row) => [
      row.batch_no,
      row.medicine_name,
      row.category,
      row.expiry_bucket,
      Number(row.days_to_expiry),
      Number(row.stock_in_hand),
      Number(row.estimated_expiry_risk_value),
    ]),
  ];
  setRangeValues(expirySheet, "F1", topRiskMatrix);
  styleTable(expirySheet, `F1:L${topRiskMatrix.length}`, "F1:L1");
  expirySheet.getRange(`L2:L${topRiskMatrix.length}`).format.numberFormat = "$#,##0.00";

  setRangeValues(dashboard, "A11", monthlyMatrix.slice(0, 8));
  styleTable(dashboard, "A11:D18", "A11:D11");
  dashboard.getRange("D12:D18").format.numberFormat = "$#,##0.00";

  setRangeValues(dashboard, "I11", categoryMatrix.slice(0, 7));
  styleTable(dashboard, "I11:L17", "I11:L11");
  dashboard.getRange("L12:L17").format.numberFormat = "$#,##0.00";

  setRangeValues(dashboard, "A21", expiryBucketMatrix);
  styleTable(dashboard, `A21:D${20 + expiryBucketMatrix.length}`, "A21:D21");
  dashboard.getRange(`D22:D${20 + expiryBucketMatrix.length}`).format.numberFormat = "$#,##0.00";

  setRangeValues(dashboard, "I21", topRiskMatrix.slice(0, 6));
  styleTable(dashboard, "I21:O26", "I21:O21");
  dashboard.getRange("O22:O26").format.numberFormat = "$#,##0.00";

  dashboard.freezePanes.freezeRows(3);

  dashboard.getRange("A29:P32").merge();
  dashboard.getRange("A29").values = [[
    `Highlights: ${category[0].category} leads category sales, expiry risk outside the 90+ day bucket totals $${formatMoney(highRiskValue)}, and the dashboard is organized for direct reporting or Power BI handoff.`,
  ]];
  dashboard.getRange("A29").format = {
    fill: "#E8EEF5",
    font: { color: theme.slate, italic: true, size: 10 },
    wrapText: true,
    verticalAlignment: "top",
  };

  dashboard.getRange("A1:P32").format.columnWidthPx = 96;
  dashboard.getRange("B:B").format.columnWidthPx = 110;
  dashboard.getRange("C:C").format.columnWidthPx = 110;
  dashboard.getRange("J:J").format.columnWidthPx = 120;
  dashboard.getRange("K:K").format.columnWidthPx = 110;
  dashboard.getRange("N:N").format.columnWidthPx = 110;

  const monthlyChartMatrix = [
    ["Month", "Gross Sales"],
    ...monthly.map((row) => [row.month, Number(row.gross_sales)]),
  ];
  setRangeValues(salesSheet, "K1", monthlyChartMatrix);
  styleTable(salesSheet, `K1:L${monthlyChartMatrix.length}`, "K1:L1");
  salesSheet.getRange(`L2:L${monthlyChartMatrix.length}`).format.numberFormat = "$#,##0.00";

  const categoryChartMatrix = [
    ["Category", "Gross Sales"],
    ...category.map((row) => [row.category, Number(row.gross_sales)]),
  ];
  setRangeValues(salesSheet, "N1", categoryChartMatrix);
  styleTable(salesSheet, `N1:O${categoryChartMatrix.length}`, "N1:O1");
  salesSheet.getRange(`O2:O${categoryChartMatrix.length}`).format.numberFormat = "$#,##0.00";

  const revenueChart = dashboard.charts.add("line", salesSheet.getRange(`K1:L${monthlyChartMatrix.length}`));
  revenueChart.title = "Monthly Sales Trend";
  revenueChart.hasLegend = false;
  revenueChart.setPosition("E11", "H18");
  revenueChart.xAxis = { axisType: "textAxis" };
  revenueChart.yAxis = { numberFormatCode: "$#,##0" };

  const categoryChart = dashboard.charts.add("bar", salesSheet.getRange(`N1:O${categoryChartMatrix.length}`));
  categoryChart.title = "Category Sales";
  categoryChart.hasLegend = false;
  categoryChart.setPosition("M11", "P18");
  categoryChart.barOptions.direction = "column";
  categoryChart.xAxis = { axisType: "textAxis" };
  categoryChart.yAxis = { numberFormatCode: "$#,##0" };

  const expiryChart = dashboard.charts.add("doughnut", expirySheet.getRange(`A1:D${expiryBucketMatrix.length}`));
  expiryChart.title = "Expiry Bucket Distribution";
  expiryChart.hasLegend = true;
  expiryChart.setPosition("E21", "H28");

  salesSheet.freezePanes.freezeRows(1);
  expirySheet.freezePanes.freezeRows(1);
  productSheet.freezePanes.freezeRows(1);

  await fs.mkdir(outputDir, { recursive: true });

  const previewBlob = await workbook.render({
    sheetName: "Dashboard",
    range: "A1:P32",
    scale: 1,
    format: "png",
  });
  await fs.writeFile(previewPath, new Uint8Array(await previewBlob.arrayBuffer()));

  const inspect = await workbook.inspect({
    kind: "table",
    range: "Dashboard!A1:P32",
    include: "values,formulas",
    tableMaxRows: 32,
    tableMaxCols: 16,
  });
  console.log(inspect.ndjson);

  const formulaErrors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: "dashboard formula scan",
  });
  console.log(formulaErrors.ndjson);

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(outputPath);
  console.log(`Saved workbook to ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
