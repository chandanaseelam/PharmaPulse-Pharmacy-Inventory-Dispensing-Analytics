# 💊 PharmaPulse — Pharmacy Inventory & Dispensing Analytics

### 📊 End-to-End Data Analytics & Business Intelligence Project

**🛠️ Technologies:** Python | SQL | SQLite | Tableau Public | Plotly  
**📅 Analysis Period:** June 2025 – August 2026  
**📁 Dataset:** Synthetic Pharmacy Operations Data

---

## 📌 About the Project

PharmaPulse is an end-to-end pharmacy analytics project I developed to explore how data can support better decisions in pharmacy operations.

A pharmacy manages multiple activities every day, including medicine inventory, customer transactions, sales, and supplier deliveries. When this information is spread across different datasets, it becomes difficult to identify inventory risks, understand sales performance, and monitor supplier reliability.

I wanted to bring these areas together and create an analytics solution that makes the information easier to understand.

For this project, I worked with 15 months of simulated pharmacy data. I used **Python** for data preparation and analysis, **SQL** to answer business questions, and **Tableau and Plotly** to build interactive dashboards.

The project focuses on inventory management, dispensing activity, revenue performance, and supplier operations.

---

## 🚀 Live Dashboards

### 📊 Tableau Public — Sales & Dispensing Analytics

**[🔗 View My Interactive Tableau Dashboards](https://public.tableau.com/app/profile/chandana.seelam/viz/PharmaPulse-PharmacySalesDispensingAnalytics/03StoreandCategoryInsights)**

**[📥 Download Tableau Workbook (.twbx)](tableau/PharmaPulse_Sales_Tableau_Window_Fixed_v2.twbx)**

I created and published three dashboards using Tableau Public.

**1. 📈 Executive Sales Overview**

Provides an overview of pharmacy sales performance, including total revenue, gross profit, units dispensed, transaction volume, and monthly trends.

**2. 💊 Dispensing and Demand**

Focuses on monthly dispensing activity, transaction patterns, and changes in medicine demand over time.

**3. 🏪 Store and Category Insights**

Compares sales and gross profit across pharmacy stores and medicine categories to understand their contributions to overall performance.

### 🌐 Interactive Pharmacy Analytics — Python & Plotly

**[🚀 Launch the Live PharmaPulse Website](https://chandanaseelam.github.io/PharmaPulse-Pharmacy-Intelligence-Analytics/)**

I also developed a separate interactive HTML dashboard using Python and Plotly.

It includes three analytical views:

- **📦 Inventory Overview:** Stock levels, reorder thresholds, low-stock conditions, and stockout patterns.
- **💰 Dispensing & Revenue Analytics:** Transactions, revenue, profit, and store performance.
- **🚚 Supply & Replenishment Risk:** Supplier delivery performance, purchasing activity, and unmet demand.

The application allows users to explore different stores, product categories, and time periods using interactive filters.

---

## 🎯 Business Problems I Wanted to Solve

I approached this project from the perspective of a Data Analyst working with a pharmacy business.

I focused on five questions:

1. Which medicines and stores experience the highest stockout risk?
2. How do revenue, profit, and dispensing activity change over time?
3. Which medicine categories and stores contribute the most to revenue?
4. How reliably are suppliers fulfilling purchase orders?
5. How can inventory monitoring and replenishment decisions be improved?

My goal was to move beyond individual transaction records and identify patterns that could support business decisions.

---

## 🔄 How I Worked on the Project

### 🐍 Step 1 — Data Preparation Using Python

I worked with synthetic datasets covering medicine information, inventory records, dispensing transactions, supplier details, and purchase orders.

Using Python, I prepared and structured the datasets, checked data quality, and validated calculations before analysis.

### 🗄️ Step 2 — Data Analysis Using SQL

I used SQL to explore the pharmacy data and answer business questions.

My analysis included filtering, joins, aggregations, and KPI calculations related to revenue, inventory availability, dispensing activity, and supplier performance.

### 📐 Step 3 — Business KPI Development

I calculated the metrics needed to understand pharmacy performance, including revenue, gross profit, gross margin, dispensed units, transaction volume, stockouts, reorder risks, and demand fulfillment.

### 📊 Step 4 — Dashboard Development

I used Plotly to visualize inventory, sales, and supplier analytics through an interactive HTML application.

I also developed three Tableau dashboards to present pharmacy sales and dispensing performance through KPI cards, trends, and business comparisons.

### ✅ Step 5 — Validation and Publishing

I used Python validation scripts to check the consistency of the project data and analytical results. The project includes documentation of 21 validation checks.

Finally, I published the Tableau workbook on Tableau Public and hosted the Plotly application using GitHub Pages.

---

## 📈 Key Results from the Data

| Business Metric | Result |
|---|---|
| 📅 Analysis Period | June 2025 – August 2026 |
| 🧾 Total Transactions | 27,314 |
| 📦 Daily Inventory Records | 34,275 |
| 💊 Units Dispensed | 49,889 |
| 💰 Total Revenue | $661,172.04 |
| 📈 Gross Profit | $218,493.34 |
| 📊 Gross Profit Margin | 33.05% |
| ⚠️ Stockout Store–Medicine–Days | 190 |
| 🔔 Below-Reorder Store–Medicine–Days | 3,629 |
| ✅ Demand Fulfillment Rate | 99.25% |

*All results represent simulated pharmacy operations.*

---

## 🔍 What I Discovered

### 💰 Sales Performance

The simulated pharmacy operations generated approximately **$661K in revenue**, with a gross profit margin of **33.05%**.

By visualizing monthly performance, I could explore how revenue and dispensing activity varied across the analysis period.

### 📦 Inventory Availability

The analysis identified **190 stockout store–medicine–days** and **3,629 below-reorder store–medicine–days**.

This demonstrated the importance of monitoring medicines before they run out rather than relying only on actual stockout records.

### 💊 Demand Fulfillment

The modeled demand fulfillment rate was **99.25%**.

Although most simulated demand was fulfilled, the remaining unmet demand provided an opportunity to investigate inventory availability and replenishment patterns.

### 🚚 Supplier Performance

I explored supplier lead times, purchase orders, and received quantities to understand how purchasing and delivery performance could affect medicine availability.

These findings represent patterns in synthetic data, not measured improvements in a real pharmacy.

---

## 🖼️ Dashboard Gallery

### 📦 Inventory Overview

![Inventory Overview](dashboards/Inventory_Dashboard_Preview.png)

### 💰 Dispensing & Revenue Analytics

![Dispensing and Revenue](dashboards/Dispensing_Revenue_Preview.png)

### 🚚 Supply & Replenishment Risk

![Supply and Replenishment Risk](dashboards/Risk_Replenishment_Preview.png)

*These screenshots represent the Plotly dashboards. The native Tableau dashboards are available through the Tableau Public link above.*

---

## 🛠️ Tools & Technologies

| Tool | How I Used It |
|---|---|
| 🐍 Python | Data generation, preparation, validation, and analysis |
| 🗄️ SQL | Business queries, joins, and aggregations |
| 💾 SQLite | Structured data storage and analysis |
| 📊 Tableau Public | Interactive sales and dispensing dashboards |
| 📈 Plotly | Interactive pharmacy analytics website |
| 🐙 GitHub | Source code and documentation |
| 🌐 GitHub Pages | Hosting the HTML dashboard |

---

## 📁 Project Structure

- `analysis/` — KPI results, business findings, and validation reports
- `dashboards/` — Dashboard previews and screenshots
- `data/` — Synthetic pharmacy datasets
- `docs/` — Project documentation and data dictionary
- `scripts/` — Python generation, analysis, and validation scripts
- `sql/` — SQL analytical queries
- `tableau/` — Tableau workbook and supporting documentation
- `index.html` — Interactive Plotly application
- `pharmacy_analytics.sqlite` — SQLite analysis database

---

## ▶️ How to Run the Project

Clone or download the GitHub repository.

**1. Validate the data**

`python3 scripts/validate_project.py`

**2. Run the analysis**

`python3 scripts/analyze.py`

**3. Install Plotly**

`python3 -m pip install plotly`

**4. Rebuild the interactive dashboard**

`python3 scripts/build_dashboard.py`

You can also open `index.html` directly in your browser.

To explore the Tableau dashboards, download the `.twbx` workbook and open it in Tableau Public Desktop.

---

## 🎓 What I Learned

This project helped me strengthen my understanding of the complete data analytics workflow, from preparing raw data to communicating business insights.

I gained practical experience working with related datasets, validating data, writing analytical SQL queries, calculating KPIs, and creating dashboards using Tableau and Python
