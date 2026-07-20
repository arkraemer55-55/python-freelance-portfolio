import requests
import json
from datetime import datetime
import os

URL = "https://open.er-api.com/v6/latest/USD"
HISTORY_FILE = "conversion_history.json"
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


def data_log(amount, target_currency, rate, conversion):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    new_entry = {
        "timestamp": timestamp,
        "usd_amount": amount,
        "target_currency": target_currency,
        "exchange_rate": rate,
        "converted_currency": round(conversion, 2),
    }
    history_log = []

    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history_log = json.load(file)
        except json.JSONDecodeError:
            history_log = []

    history_log.append(new_entry)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history_log, file, indent=4)

    print(f"Conversion Logged to {HISTORY_FILE}")


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
            data_log(amount, target_currency, rate, conversion)
            break


if __name__ == "__main__":
    currency_converter()
