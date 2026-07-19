import csv
import json

CSV_FILE = "raw_sales.csv"
JSON_OUTPUT = "clean_report.json"


def data_cleaner():
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            row["item"] = row["item"].strip().title()
            if row["customer_name"] == "":
                row["customer_name"] = "Unknown Customer"
            else:
                row["customer_name"] = row["customer_name"].strip().title()

            try:
                row["quantity"] = int(row["quantity"])
            except ValueError:
                print(
                    f"WARNING Missing Quantity Data for transaction {row['transaction_id']}"
                )
                continue

            try:
                row["unit_price"] = f"{float(row['unit_price']):.2f}"
            except ValueError:
                print(
                    f"WARNING: Invalid Unit Price in transaction: {row['transaction_id']}"
                )
                continue

            print(row["transaction_id"])
            print(f"{row['customer_name']}")
            print(f"{row['item']}")
            print(f"{row['quantity']}")
            print(row["unit_price"])


if __name__ == "__main__":
    data_cleaner()
