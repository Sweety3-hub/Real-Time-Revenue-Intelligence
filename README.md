# Real-Time Revenue Leakage & Customer Journey Intelligence

Portfolio project using simulated e-commerce data.

## Project Overview

This project analyzes simulated e-commerce data to identify payment failures, customer journey drop-offs, product returns, shipping delays, and potential revenue risks.

It uses PostgreSQL, Python, SQL, Power BI, and Streamlit to convert data into useful business insights.

## Objectives

- Analyze customer journey and conversion rates.
- Identify failed payments and unusual transactions.
- Analyze product returns and shipping delays.
- Estimate potential revenue at risk.
- Generate business recommendations.
- Present insights through an interactive dashboard.

## Technology Stack

- **Database:** PostgreSQL
- **Programming:** Python
- **Data Analysis:** Pandas and SQL
- **Visualization:** Power BI and Streamlit
- **Version Control:** Git and GitHub

## Project Structure

- `python/` — Data generation, analysis, anomaly detection, and recommendations.
- `sql/` — SQL queries for business analysis.
- `powerbi/` — Power BI dashboard.
- `streamlit_app/` — Streamlit dashboard.
- `Portfolio Project.pptx` — Project presentation.

## Key Analysis Areas

1. Customer journey and conversion funnel.
2. Payment success and failure analysis.
3. Revenue and potential payment risk.
4. Product returns.
5. Shipment delays.
6. Payment anomaly detection.
7. Business recommendations.

## Key Findings

- **Completed Sales:** ₹870,887.01
- **Net Sales After Refunds:** ₹754,415.20
- **Failed Payment Attempts:** 21
- **Potential Payment Risk:** ₹151,989.12
- **Delivery Delay Rate:** 54.87%
- **Payment Anomalies Flagged:** 7

These findings are based on simulated data.

## How to Run

1. Install Python and PostgreSQL.
2. Configure the project database and required tables.
3. Install the required Python packages.
4. Set the PostgreSQL password using an environment variable.
5. Open a terminal in the project folder.
6. Activate the virtual environment:

   `.\.venv\Scripts\Activate.ps1`

7. Start the dashboard:

   `python -m streamlit run streamlit_app/app.py`

The dashboard requires a correctly configured PostgreSQL database.

## Data and Limitations

This project uses simulated e-commerce data. Failed payment amounts represent potential revenue at risk, not confirmed lost revenue. Anomaly flags identify transactions for investigation and do not prove fraud.

## Future Improvements

- Automate data refresh.
- Improve anomaly detection.
- Expand customer journey analysis.
- Add more business KPIs and filters.

## Author

Keerthi Reddy

## Dashboard Preview

Dashboard screenshots will be added here soon.