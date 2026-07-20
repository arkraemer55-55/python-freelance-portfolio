import sqlite3
from datetime import datetime
import requests

URL = "https://open.er-api.com/v6/latest/USD"
DB_FILE = "tracker_database.db"
SYMBOLS = {
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CHF": "₣",
    "AUD": "$",
    "INR": "₹",
    "MXN": "$",
    "USD": "$",
    "CAD": "$",
}


def main_menu():
    init_db()

    while True:
        print("\n=== CURRENCY TERMINAL & DATABASE===")
        print("1. Convert Currency")
        print("2. View Conversion History")
        print("3. View Analytics and Insights")
        print("4. EXIT")

        choice = input("Select and option (1-4): ").strip()

        if choice == "1":
            currency_converter()
        elif choice == "2":
            logs = fetch_history_db()
            print("\n ---DATABASE HISTORY LOGS---")
            if not logs:
                print("No conversions found in history.")
            else:
                for log in logs:
                    print(
                        f"ID: {log[0]} | Date: {log[1]} | ${log[2]:.2f} USD -> {log[5]:.2f} {log[3]}"
                    )
        elif choice == "3":
            count, total_usd, avg_usd, max_usd = get_analytics_summary_db()

            print("\n=== DATABASE ANALYTICS SUMMARY ===")
            print(f"Total Transactions:   {count}")
            print(f"Total USD Converted:  ${total_usd:.2f}")
            print(f"Average USD Amount:   ${avg_usd:.2f}")
            print(f"Largest Transaction:  ${max_usd:.2f}")

            breakdown = get_currency_breakdown()
            print("\n--- CURRENCY BREAKDOWN ---")
            if not breakdown:
                print("No data available.")
            else:
                for currency, total_count, total_amount in breakdown:
                    print(
                        f"{currency}: {total_count} transaction(s) | Total: ${total_amount:.2f}"
                    )

        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


def fetch_rates():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})
        else:
            print(f"Error: server responded with status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Network error: Could not connect to the API. ({e})")
        return None


def currency_converter():
    print("Connecting to the financial markets to pull USD rates...")
    rates = fetch_rates()
    if not rates:
        print(
            "Unable to load exchange rates. Please check your connection and try again."
        )
        return
    amount = 0
    while True:
        try:
            amount = float(input("How many USD do you want to convert: "))
        except ValueError:
            print("Invalid value. Please try again.")
            continue
        target_currency = (
            input("What target currency code (e.g., CAD, EUR): ").strip().upper()
        )
        if target_currency not in rates:
            print("Invalid currency. Please try again.")
            continue
        else:
            if target_currency in SYMBOLS:
                cur_symb = SYMBOLS[target_currency]
            else:
                cur_symb = ""
            rate = rates[target_currency]
            conversion = amount * rate
            print(
                f"USD to {target_currency}= {cur_symb}{conversion:.2f} {target_currency}"
            )
            log_conversion_db(amount, target_currency, rate, conversion)
            break


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        usd_amount REAL NOT NULL,
        target_currency TEXT NOT NULL,
        exchange_rate REAL NOT NULL,
        converted_amount REAL NOT NULL
    );
    """
    )
    conn.commit()
    conn.close()
    print("Success!")


def log_conversion_db(amount, target_currency, rate, conversion):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO conversions (timestamp, usd_amount, target_currency, exchange_rate, converted_amount)
        VALUES (?, ?, ?, ?, ?);
        """,
        (timestamp, amount, target_currency, rate, conversion),
    )
    conn.commit()
    conn.close()
    print("Conversion logged to database")


def fetch_history_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversions ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_analytics_summary_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT
                        COUNT(*),
                        COALESCE(SUM(usd_amount),0),
                        COALESCE(AVG(usd_amount),0),
                        COALESCE(MAX(usd_amount),0)
                   FROM conversions;
                   """)
    stats = cursor.fetchone()
    conn.close()
    return stats


def get_currency_breakdown():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
                    SELECT
                        target_currency,
                        COUNT(*),
                        SUM(converted_amount)
                    FROM conversions
                    GROUP BY target_currency
                    ORDER BY COUNT(*) DESC;
                   """)
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    main_menu()
