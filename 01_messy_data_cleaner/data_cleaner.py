import csv
import json

CSV_FILE = "raw_sales.csv"
JSON_OUTPUT = "clean_report.json"


def data_cleaner():
    clean_data = {"gross_revenue": [], "successful_transaction": [], "item": []}
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        gross_unit_price = 0
        gross_quantity = 0
        gross_revenue = 0
        successful_transaction = 0
        items = {}
        for row in csv_reader:
            transaction_id = row["transaction_id"]
            item = row["item"].strip().title()
            if row["customer_name"] == "":
                customer_name = "Unknown Customer"
            else:
                customer_name = row["customer_name"].strip().title()

            try:
                quantity = int(row["quantity"])
            except ValueError:
                print(
                    f"WARNING Missing Quantity Data for transaction {row['transaction_id']}\n"
                )
                continue

            try:
                unit_price = float(row["unit_price"])
            except ValueError:
                print(
                    f"WARNING: Invalid Unit Price in transaction: {row['transaction_id']}\n"
                )
                continue
            gross_quantity += quantity
            gross_unit_price += unit_price
            revenue = quantity * unit_price
            gross_revenue += revenue
            successful_transaction += 1
            items[item] = items.get(item, 0)
            items[item] += 1

            print(f"Transaction: {transaction_id}")
            print(f"Name: {customer_name}")
            print(f"Item: {item}")
            print(f"Days rented: {quantity}")
            print(f"Price: {unit_price}\n")

    clean_data = {
        "report_summary": {
            "gross_revenue": gross_revenue,
            "successful_transactions": successful_transaction,
        },
        "items_sold_distribution": items,
    }
    print(clean_data)
    with open(JSON_OUTPUT, "w", encoding="utf-8") as out_file:
        json.dump(clean_data, out_file, indent=4)


if __name__ == "__main__":
    data_cleaner()
