# Real-Time Revenue Leakage & Customer Journey Intelligence

## Project Overview
This portfolio project analyzes simulated e-commerce data to identify payment failures, customer journey drop-offs, product returns, shipping delays, and potential revenue risks.

The project combines SQL, Python, Power BI, and Streamlit to turn transactional data into useful business insights.

## Objectives
- Analyze customer journey events and conversion rates.
- Identify failed payments and flag unusual transactions.
- Measure product returns and shipping delays.
- Estimate potential revenue at risk from failed payment attempts.
- Generate business recommendations based on analytical findings.
- Present insights through an interactive dashboard.

## Technology Stack
- **Database:** PostgreSQL
- **Programming:** Python
- **Data Analysis:** Pandas and SQL
- **Visualization:** Power BI and Streamlit
- **Version Control:** Git and GitHub

## Project Structure
- `python/` — Data generation, revenue analysis, anomaly detection, and recommendations.
- `sql/` — SQL queries for business analysis.
- `powerbi/` — Power BI dashboard.
- `streamlit_app/` — Interactive Streamlit dashboard.
- `documentation/` — Supporting project documentation.
- `Portfolio Project.pptx` — Project presentation.

## Key Analysis Areas
1. Customer journey and conversion funnel.
2. Payment success and failure analysis.
3. Revenue analysis and potential revenue at risk.
4. Product return analysis.
5. Shipment delay analysis.
6. Transaction anomaly detection.
7. Data-driven business recommendations.

## How to Run
1. Install Python and PostgreSQL.
2. Create and configure the project database.
3. Install the required Python packages.
4. Configure database connection settings using environment variables.
5. Run the relevant data-generation scripts only when you intend to create or refresh the simulated data.
6. Launch the Streamlit application from the project root using:

   `streamlit run streamlit_app/app.py`

The application requires the database and its expected tables to be configured correctly before it can load data.

## Data and Limitations
This project uses simulated e-commerce data for learning and portfolio demonstration. Payment anomaly flags indicate transactions that may deserve further investigation; they do not establish fraud. Failed payment amounts represent potential revenue at risk, not confirmed lost revenue.

## Future Improvements
- Add automated data refresh and monitoring.
- Improve anomaly detection and evaluation.
- Expand customer journey analysis.
- Add more detailed business KPIs and dashboard filters.

## Author
Keerthi Reddy
