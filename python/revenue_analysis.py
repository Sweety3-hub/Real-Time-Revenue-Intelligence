
import os
import pandas as pd
from sqlalchemy import create_engine, URL

# Connect securely to the existing PostgreSQL database
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=os.environ["PGPASSWORD"],
    host="localhost",
    port=5432,
    database="revenue_intelligence",
)

engine = create_engine(db_url)

try:
    # Load transaction data for analysis
    payments = pd.read_sql_query(
        "SELECT * FROM payments", engine
    )

    orders = pd.read_sql_query(
        "SELECT * FROM orders", engine
    )

    returns = pd.read_sql_query(
        "SELECT * FROM returns", engine
    )

    # Calculate key business metrics
    successful_payments = payments[
        payments["payment_status"] == "Success"
    ]

    failed_payments = payments[
        payments["payment_status"] == "Failed"
    ]

    completed_orders = orders[
        orders["order_status"] == "Completed"
    ]

    failed_amount = failed_payments[
        "transaction_amount"
    ].sum()

    refund_amount = returns["refund_amount"].sum()

    completed_sales = completed_orders[
        "total_amount"
    ].sum()

    print("\n=== REVENUE INTELLIGENCE ANALYSIS ===")

    print(f"Total orders: {len(orders)}")
    print(f"Completed orders: {len(completed_orders)}")
    print(f"Successful payments: {len(successful_payments)}")
    print(f"Failed payment attempts: {len(failed_payments)}")

    print(f"\nCompleted sales: ₹{completed_sales:,.2f}")
    print(f"Successful payment amount: "
          f"₹{successful_payments['transaction_amount'].sum():,.2f}")
    print(f"Failed payment amount at risk: ₹{failed_amount:,.2f}")
    print(f"Total refunds: ₹{refund_amount:,.2f}")

    print("\nNote: Failed payment amount is potential revenue at risk,")
    print("not confirmed lost revenue.")

    # Show the failed payment methods for further analysis
    print("\n=== FAILED PAYMENTS BY METHOD ===")

    failure_summary = (
        failed_payments
        .groupby("payment_method")
        .agg(
            failed_attempts=("payment_id", "count"),
            amount_at_risk=("transaction_amount", "sum"),
        )
        .reset_index()
        .sort_values("amount_at_risk", ascending=False)
    )

    print(failure_summary.to_string(index=False))

except Exception as error:
    print("Analysis failed:", error)

finally:
    engine.dispose()
