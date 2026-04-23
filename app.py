import os
from flask import Flask, request, redirect, render_template
import psycopg2
from scraper_utils import scrape_amazon_product, update_product_data

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)
@app.route("/")
def dashboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, amazon_url, title, price_text, stock_status, checked_at, main_image_url
        FROM products
        ORDER BY id DESC
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("dashboard.html", products=products)

@app.route("/scraping")
def scraping_page():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, amazon_url, title, price_text, stock_status, checked_at, main_image_url
        FROM products
        ORDER BY id DESC
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("scraping.html", products=products)

@app.route("/add", methods=["POST"])
def add():
    amazon_url = request.form["amazon_url"].strip()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (amazon_url)
        VALUES (%s)
        ON CONFLICT (amazon_url) DO NOTHING
    """, (amazon_url,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/scraping")

@app.route("/scrape/<int:product_id>")
def scrape_one(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT amazon_url FROM products WHERE id = %s", (product_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        data = scrape_amazon_product(row[0], DATABASE_URL)
        update_product_data(product_id, data, DATABASE_URL)

    return redirect("/scraping")

@app.route("/scrape-all")
def scrape_all():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, amazon_url FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    for product_id, amazon_url in rows:
        data = scrape_amazon_product(amazon_url, DATABASE_URL)
        update_product_data(product_id, data, DATABASE_URL)

    return redirect("/scraping")

if __name__ == "__main__":
    app.run(debug=True)