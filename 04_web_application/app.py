import sqlite3
from flask import Flask, render_template


app = Flask(__name__)
DB_FILE = "../03_database_integration/tracker_database.db"


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


@app.route("/")
def home():
    count, total_usd, avg_usd, max_usd = get_analytics_summary_db()
    breakdown = get_currency_breakdown()

    return render_template(
        "index.html",
        title="Currency Portfolio Dashboard",
        count=count,
        total_usd=total_usd,
        avg_usd=avg_usd,
        max_usd=max_usd,
        breakdown=breakdown,
    )


if __name__ == "__main__":
    app.run(debug=True)
