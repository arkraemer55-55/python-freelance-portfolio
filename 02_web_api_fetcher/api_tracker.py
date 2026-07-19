import requests

URL = "https://open.er-api.com/v6/latest/USD"

# print("Fetching live exchange rates from the financial markets...")
response = requests.get(URL)
data = response.json()

rates = data.get("rates", {})

# print("\n--- LIVE USD CONVERSIONS ---")
# print(f"1 USD = {rates.get('EUR')} Euros (EUR)")
# print(f"1 USD = {rates.get('CAD')} Canadian Dollars (CAD)")
# print(f"1 USD = {rates.get('GBP')} British Pounds (GBP)")


def currency_converter():
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
        if target_currency not in data.get("rates", {}):
            print("Invalid currency. Please try again.")
            continue
        else:
            conversion = amount * float(rates.get(target_currency))
            print(f"USD to {target_currency}= {conversion:.2f} {target_currency}")
            break


if __name__ == "__main__":
    currency_converter()
