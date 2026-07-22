import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/USD"


app = Flask(__name__)
app.secret_key = "super-secret-key-for-dev"
DB_FILE = "../03_database_integration/tracker_database.db"


def fetch_exchange_rate(target_currency):
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=5)
        data = response.json()

        if response.status_code == 200 and data.get("result") == "success":
            rates = data.get("rates", {})
            return rates.get(target_currency.upper())
    except Exception as e:
        print(f"Error fetching enchange rate {e}")
    return None


def get_analytics_summary_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*), 
            COALESCE(SUM(usd_amount), 0), 
            COALESCE(AVG(usd_amount), 0), 
            COALESCE(MAX(usd_amount), 0) 
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


def insert_conversion(usd, currency, converted, rate):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversions (usd_amount, target_currency, converted_amount, exchange_rate, timestamp)
            VALUES (?, ?, ?, ?, ?);
            """,
            (usd, currency, converted, rate, timestamp),
        )


def get_recent_conversions(limit=10):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT usd_amount, target_currency, converted_amount, exchange_rate, timestamp
            FROM conversions
            ORDER BY id DESC
            LIMIT ?;
        """,
            (limit,),
        )
        return cursor.fetchall()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        usd = float(request.form["usd_amount"])
        currency = request.form["target_currency"].upper()
        rate = fetch_exchange_rate(currency)

        if rate is None:
            flash(
                f"Error: Could not fetch exchange rate for '{currency}'. Check the currency code!",
                "error",
            )
            return redirect(url_for("home"))

        converted = usd * rate
        insert_conversion(usd, currency, converted, rate)
        flash(
            f"Succussfully converted ${usd:,.2f} USD to {converted:,.2f} {currency} at {rate}!",
            "success",
        )
        return redirect(url_for("home"))

    count, total_usd, avg_usd, max_usd = get_analytics_summary_db()
    breakdown = get_currency_breakdown()
    recent = get_recent_conversions()

    return render_template(
        "index.html",
        title="Currency Portfolio Dashboard",
        count=count,
        total_usd=total_usd,
        avg_usd=avg_usd,
        max_usd=max_usd,
        breakdown=breakdown,
        recent=recent,
    )


if __name__ == "__main__":
    app.run(debug=True)
