
import os
import pandas as pd
from sqlalchemy import create_engine, URL

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
    payments = pd.read_sql_query(
        "SELECT * FROM payments", engine
    )
    shipments = pd.read_sql_query(
        "SELECT * FROM shipments", engine
    )
    returns = pd.read_sql_query(
        "SELECT * FROM returns", engine
    )

    recommendations = []

    failed = payments[
        payments["payment_status"] == "Failed"
    ]

    failed_amount = failed["transaction_amount"].sum()

    if not failed.empty:
        method_summary = (
            failed.groupby("payment_method")["transaction_amount"]
            .agg(["count", "sum"])
            .sort_values("sum", ascending=False)
        )

        top_method = method_summary.index[0]
        top_amount = method_summary.iloc[0]["sum"]

        recommendations.append({
            "area": "Payments",
            "finding": (
                f"{len(failed)} failed payment attempts totaling "
                f"₹{failed_amount:,.2f}"
            ),
            "recommendation": (
                f"Investigate payment failures by method, starting "
                f"with {top_method}, which has ₹{top_amount:,.2f} "
                f"in failed attempts. Review gateway logs and retry "
                f"behavior before changing payment settings."
            ),
            "priority": "High",
        })

    if not shipments.empty:
        delayed = shipments[
            shipments["shipment_status"] == "Delayed"
        ]
        delay_rate = len(delayed) / len(shipments) * 100

        recommendations.append({
            "area": "Delivery",
            "finding": (
                f"{len(delayed)} of {len(shipments)} shipments "
                f"are marked delayed ({delay_rate:.2f}%)."
            ),
            "recommendation": (
                "Review shipping-partner performance, dispatch times, "
                "and delivery estimates. Investigate repeated delays."
            ),
            "priority": "High" if delay_rate >= 20 else "Medium",
        })

    if not returns.empty:
        reason_summary = (
            returns.groupby("return_reason")["refund_amount"]
            .agg(["count", "sum"])
            .sort_values("count", ascending=False)
        )

        top_reason = reason_summary.index[0]
        top_count = int(reason_summary.iloc[0]["count"])

        recommendations.append({
            "area": "Returns",
            "finding": (
                f"{len(returns)} returns totaling "
                f"₹{returns['refund_amount'].sum():,.2f} in refunds."
            ),
            "recommendation": (
                f"Investigate the most frequent recorded return reason: "
                f"{top_reason} ({top_count} returns). Check product "
                f"quality and listing accuracy."
            ),
            "priority": "Medium",
        })

    result = pd.DataFrame(recommendations)

    print("\n=== BUSINESS RECOMMENDATIONS ===\n")
    print(result.to_string(index=False))

    output_path = os.path.join(
        os.path.dirname(__file__),
        "business_recommendations.csv"
    )
    result.to_csv(output_path, index=False)

    print(f"\nSaved recommendations to: {output_path}")

finally:
    engine.dispose()
