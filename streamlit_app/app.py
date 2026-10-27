
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import URL, create_engine, text

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Revenue Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("Real-Time Revenue Leakage & Customer Journey Intelligence")
st.caption(
    "Portfolio demonstration using simulated e-commerce data."
)


# --------------------------------------------------
# Load data from CSV files or local PostgreSQL
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_ROOT / "data" / "dashboard_csvs"

REQUIRED_CSVS = [
    "orders.csv",
    "payments.csv",
    "returns.csv",
    "shipments.csv",
    "events.csv",
]


@st.cache_data(ttl=60)
def load_csv_data():
    return (
        pd.read_csv(CSV_DIR / "orders.csv"),
        pd.read_csv(CSV_DIR / "payments.csv"),
        pd.read_csv(CSV_DIR / "returns.csv"),
        pd.read_csv(CSV_DIR / "shipments.csv"),
        pd.read_csv(CSV_DIR / "events.csv"),
    )


@st.cache_data(ttl=60)
def load_postgres_data():
    password = os.getenv("PGPASSWORD")

    if not password:
        raise RuntimeError(
            "PostgreSQL password is missing. "
            "Set PGPASSWORD to use the local database."
        )

    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="revenue_intelligence",
    )

    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            orders = pd.read_sql_query(
                text("SELECT * FROM orders"), connection
            )
            payments = pd.read_sql_query(
                text("SELECT * FROM payments"), connection
            )
            returns = pd.read_sql_query(
                text("SELECT * FROM returns"), connection
            )
            shipments = pd.read_sql_query(
                text("SELECT * FROM shipments"), connection
            )
            events = pd.read_sql_query(
                text("SELECT * FROM events"), connection
            )

        return orders, payments, returns, shipments, events

    finally:
        engine.dispose()


try:
    if all(
        (CSV_DIR / filename).is_file()
        for filename in REQUIRED_CSVS
    ):
        orders, payments, returns, shipments, events = (
            load_csv_data()
        )
        st.caption("Data source: CSV snapshots")
    else:
        orders, payments, returns, shipments, events = (
            load_postgres_data()
        )
        st.caption("Data source: PostgreSQL database")

except Exception as error:
    st.error(f"Could not load dashboard data: {error}")
    st.stop()


# --------------------------------------------------
# Calculate key metrics
# --------------------------------------------------
completed_orders = orders[
    orders["order_status"] == "Completed"
]

failed_payments = payments[
    payments["payment_status"] == "Failed"
]

completed_sales = completed_orders["total_amount"].sum()
total_refunds = returns["refund_amount"].sum()
net_sales = completed_sales - total_refunds
failed_amount = failed_payments["transaction_amount"].sum()

delayed_count = (
    shipments["shipment_status"] == "Delayed"
).sum()

delay_rate = (
    delayed_count / len(shipments) * 100
    if len(shipments) > 0 else 0
)

# --------------------------------------------------
# KPI cards
# --------------------------------------------------
st.subheader("Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Completed Sales", f"₹{completed_sales:,.2f}")
c2.metric("Net Sales After Refunds", f"₹{net_sales:,.2f}")
c3.metric("Failed Payment Attempts", f"{len(failed_payments):,}")
c4.metric("Potential Payment Risk", f"₹{failed_amount:,.2f}")

c5, c6, c7 = st.columns(3)

c5.metric("Total Orders", f"{len(orders):,}")
c6.metric("Total Refunds", f"₹{total_refunds:,.2f}")
c7.metric("Delivery Delay Rate", f"{delay_rate:.2f}%")

st.divider()

# --------------------------------------------------
# Payment analysis
# --------------------------------------------------
st.subheader("Payment Performance")

left, right = st.columns(2)

with left:
    st.markdown("**Failed Payment Amount by Method**")

    if failed_payments.empty:
        st.info("No failed payments found.")
    else:
        method_summary = (
            failed_payments
            .groupby("payment_method")["transaction_amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(method_summary)

with right:
    st.markdown("**Payment Status Distribution**")

    payment_counts = (
        payments["payment_status"]
        .value_counts()
        .rename_axis("Payment Status")
        .reset_index(name="Count")
    )

    st.bar_chart(
        payment_counts.set_index("Payment Status")["Count"]
    )

# --------------------------------------------------
# Customer journey
# --------------------------------------------------
st.subheader("Customer Journey")

journey_types = [
    "product_view",
    "add_to_cart",
    "checkout_start",
]

journey = (
    events[events["event_type"].isin(journey_types)]
    .groupby("event_type")["session_id"]
    .nunique()
    .reindex(journey_types, fill_value=0)
)

journey.index = [
    "Product Views",
    "Add to Cart",
    "Checkout Started",
]

st.bar_chart(journey)

view_count = int(journey.iloc[0])
cart_count = int(journey.iloc[1])
checkout_count = int(journey.iloc[2])

if view_count > 0:
    st.write(
        f"View-to-cart rate: {cart_count / view_count * 100:.2f}%"
    )
    st.write(
        f"View-to-checkout rate: "
        f"{checkout_count / view_count * 100:.2f}%"
    )

# --------------------------------------------------
# Delivery and returns
# --------------------------------------------------
st.subheader("Delivery & Returns")

left, right = st.columns(2)

with left:
    st.markdown("**Shipment Status**")

    if shipments.empty:
        st.info("No shipment records found.")
    else:
        shipment_counts = (
            shipments["shipment_status"]
            .value_counts()
        )
        st.bar_chart(shipment_counts)

with right:
    st.markdown("**Refund Amount by Return Reason**")

    if returns.empty:
        st.info("No return records found.")
    else:
        refund_summary = (
            returns.groupby("return_reason")["refund_amount"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(refund_summary)

# --------------------------------------------------
# Anomaly detection results
# --------------------------------------------------
st.subheader("Payment Anomaly Detection")

anomaly_file = (
    Path(__file__).resolve().parent.parent
    / "python"
    / "payment_anomalies.csv"
)

if anomaly_file.exists():
    anomalies = pd.read_csv(anomaly_file)

    if "anomaly_flag" in anomalies.columns:
        unusual = anomalies[
            anomalies["anomaly_flag"] == -1
        ]

        st.write(
            f"Unusual payment records flagged: {len(unusual)}"
        )

        if not unusual.empty:
            display_columns = [
                "payment_id",
                "payment_method",
                "payment_status",
                "transaction_amount",
                "anomaly_result",
            ]

            st.dataframe(
                unusual[display_columns],
                use_container_width=True,
            )
    else:
        st.info(
            "The anomaly CSV has no anomaly flags. "
            "Run anomaly_detection.py again."
        )
else:
    st.info(
        "Run python/anomaly_detection.py to generate "
        "the anomaly results."
    )

st.caption(
    "This application uses simulated data. "
    "Flagged anomalies require investigation and do not prove fraud."
)
