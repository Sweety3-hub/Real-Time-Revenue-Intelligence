
import os
import pandas as pd
from sqlalchemy import create_engine, URL
from sklearn.ensemble import IsolationForest

# Connect to PostgreSQL securely
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
    # Load payment attempts from the database
    query = """
        SELECT
            payment_id,
            order_id,
            customer_id,
            payment_method,
            payment_status,
            transaction_amount
        FROM payments
        WHERE transaction_amount IS NOT NULL
          AND transaction_amount > 0
    """

    payments = pd.read_sql_query(query, engine)

    if len(payments) < 10:
        print("Not enough payment records for reliable anomaly detection.")
    else:
        # Learn unusual patterns from transaction amounts
        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        payments["anomaly_flag"] = model.fit_predict(
            payments[["transaction_amount"]]
        )

        payments["anomaly_result"] = payments["anomaly_flag"].map({
            1: "Normal",
            -1: "Unusual - Investigate"
        })

        unusual = payments[
            payments["anomaly_flag"] == -1
        ].sort_values(
            "transaction_amount", ascending=False
        )

        print("\n=== PAYMENT ANOMALY DETECTION ===")
        print(f"Payment records analyzed: {len(payments)}")
        print(f"Unusual records flagged: {len(unusual)}")

        print("\n=== UNUSUAL PAYMENT ATTEMPTS ===")

        if unusual.empty:
            print("No unusual payment attempts detected.")
        else:
            print(
                unusual[
                    [
                        "payment_id",
                        "order_id",
                        "payment_method",
                        "payment_status",
                        "transaction_amount",
                        "anomaly_result",
                    ]
                ].to_string(index=False)
            )

        # Save results for review
        output_path = os.path.join(
            os.path.dirname(__file__),
            "payment_anomalies.csv"
        )

        payments.to_csv(output_path, index=False)
        print(f"\nFull results saved to: {output_path}")

        print(
            "\nNote: A flagged transaction is unusual, "
            "not necessarily fraudulent."
        )

finally:
    engine.dispose()
