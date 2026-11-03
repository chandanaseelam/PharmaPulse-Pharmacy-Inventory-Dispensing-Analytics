# PharmaPulse — Pharmacy Inventory & Dispensing Analytics

**End-to-end Data Analytics portfolio project**  
**Tech stack:** Python · SQL · Tableau Public · Plotly · SQLite  
**Coverage:** June 2025 – August 2026 · **Data:** fully synthetic pharmacy operations

## Live dashboards

### Interactive pharmacy analytics (Plotly)

🚀 **[Launch the live PharmaPulse website](https://chandanaseelam.github.io/PharmaPulse-Pharmacy-Intelligence-Analytics/)**

This interactive HTML application includes three views:

1. **Inventory Overview** — stock levels, low-stock flags, reorder thresholds, and stockouts.
2. **Dispensing & Revenue Analytics** — transactions, demand, modeled revenue, profit, and store comparisons.
3. **Supply & Replenishment Risk** — supplier performance, purchasing, and unfulfilled modeled demand.

The HTML dashboard is powered by Plotly. It is a separate application from the Tableau Public workbook.

### Tableau Public — Sales & Dispensing Analytics

📊 **[Open the published Tableau workbook](https://public.tableau.com/app/profile/chandana.seelam/viz/PharmaPulse-PharmacySalesDispensingAnalytics/03StoreandCategoryInsights)**

The Tableau workbook contains **three published dashboards**:

1. **Executive Sales Overview** — revenue, gross profit, units dispensed, transaction KPIs, and trends.
2. **Dispensing and Demand** — transaction and dispensing trends.
3. **Store and Category Insights** — store and product-category comparisons.

**[Download the Tableau workbook (.twbx)](tableau/PharmaPulse_Sales_Tableau_Window_Fixed_v2.twbx)** — verified to open in Tableau Public Desktop by the project author and published on Tableau Public. It includes its own Tableau sales extract. The Tableau workbook currently covers sales and dispensing, **not** the inventory or supplier views from the Plotly website.

## Dashboard gallery — interactive HTML application

### Inventory Overview
![Inventory overview screenshot](dashboards/Inventory_Dashboard_Preview.png)

### Dispensing & Revenue
![Dispensing and revenue screenshot](dashboards/Dispensing_Revenue_Preview.png)

### Supply & Replenishment Risk
![Supply and replenishment screenshot](dashboards/Risk_Replenishment_Preview.png)

## Key simulated business metrics

| Metric | Result |
|:---|---:|
| Analysis period | June 2025–August 2026 |
| Simulated transactions | 27,314 |
| Daily inventory records | 34,275 |
| Units dispensed | 49,889 |
| Modeled revenue | $661,172.04 |
| Modeled gross profit | $218,493.34 |
| Modeled gross margin | 33.05% |
| Stockout store–medicine–days | 190 |
| Below-reorder store–medicine–days | 3,629 |
| Demand fulfillment rate | 99.25% |

These are simulated outcomes, not measured changes in a real pharmacy.

## Business questions

- Which stores and products show the highest stockout and low-stock exposure?
- How do revenue, profit, transactions, and dispensing volume change over time?
- Which product categories and locations contribute most to modeled revenue?
- Which synthetic suppliers have lower on-time delivery performance?
- How can replenishment and stock monitoring be prioritized?

## Data and analytical workflow

**Synthetic data generation → validation/cleaning → SQL and Python analysis → KPI computation → Plotly and Tableau dashboards → business interpretation**

Refer to [`analysis/Business_Findings.md`](analysis/Business_Findings.md) for scenario findings and caveats; [`docs/Data_Dictionary.md`](docs/Data_Dictionary.md) for field definitions; and [`tableau/README.md`](tableau/README.md) for Tableau workbook details.

## Repository contents

| Path | Purpose |
|:---|:---|
| `index.html` | GitHub Pages entry point and live Plotly dashboard |
| `dashboards/` | HTML dashboard and three preview screenshots |
| `tableau/` | Working `.twbx`, Tableau screenshot, and additional calculated-field guidance |
| `data/` | Synthetic pharmacy transactions, snapshots, demand, supplier records, dimensions |
| `analysis/` | Business findings, KPIs, analysis outputs, validation report |
| `scripts/` | Python scripts to generate, validate, analyze, and build dashboards |
| `sql/` | SQL business analysis queries |
| `docs/` | Project description, roadmap, data dictionary and resume guidance |
| `pharmacy_analytics.sqlite` | SQLite analysis database |

## Reproduce the analysis

With Python 3, run from the repository root:

```bash
python3 scripts/validate_project.py
python3 scripts/analyze.py
```

To rebuild the Plotly HTML dashboard from the included data:

```bash
python3 -m pip install plotly
python3 scripts/build_dashboard.py
```

To open the Tableau workbook, download `tableau/PharmaPulse_Sales_Tableau_Window_Fixed_v2.twbx` and open it in Tableau Public Desktop. The embedded extract is packaged with the workbook.

## Publishing notes

GitHub Pages uses `index.html` in the repository root. After uploading the files, visit **Settings → Pages → Deploy from a branch → main / (root)**. Tableau Public is hosted independently at the link above.

## Data disclaimer

**All data is synthetic and used only for education and portfolio demonstration.** Results are not actual pharmacy operations, clinical evidence, or proven business improvements. Financial values are modeled. Images in the HTML gallery depict the Plotly app, not native Tableau dashboards.
