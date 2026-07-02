from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from recommendor import ContentRecommender
import uuid
import os

import create_db

DB_PATH = "restaurants.db"
app = Flask(__name__)
app.secret_key = os.urandom(24)


def ensure_database():
    """Build restaurants.db (and the reservations table) automatically if
    they don't exist yet, so the app runs out of the box without requiring
    the user to manually run the setup scripts first."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurants'")
    has_restaurants = cur.fetchone() is not None
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reservations'")
    has_reservations = cur.fetchone() is not None
    conn.close()

    if not has_restaurants:
        create_db.build_database()
    if not has_reservations:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                restaurant TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                people INTEGER NOT NULL,
                cuisine TEXT,
                city TEXT
            )
        """)
        conn.commit()
        conn.close()


ensure_database()
reco = ContentRecommender(DB_PATH)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
    "Jaipur", "Pune", "Ahmedabad", "Lucknow", "Chandigarh", "Goa",
    "Indore", "Bhopal", "Surat", "Shimla", "Ranchi"
]
CUISINES = [
    "North Indian", "South Indian", "Chinese", "Italian",
    "Street Food", "Continental", "Seafood", "Awadhi"
]
VEG_TYPES = ["Any", "Veg", "Non-Veg", "Both"]
PRICE_RANGES = ["Any", "Budget", "Mid-Range", "Premium"]
OCCASIONS = ["", "romantic", "family-friendly", "quick-bite", "fine-dining", "kid-friendly"]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form["city"]
        cuisine = request.form["cuisine"]
        veg_type = request.form.get("veg_type") or None
        price_range = request.form.get("price_range") or None
        occasion = request.form.get("occasion") or None
        phone = request.form.get("phone") or None

        if veg_type == "Any":
            veg_type = None
        if price_range == "Any":
            price_range = None

        recommendations = reco.recommend(
            city=city,
            cuisine=cuisine,
            veg_type=veg_type,
            price_range=price_range,
            occasion=occasion,
            phone=phone,
            top_n=3,
        )

        return render_template(
            "recommend.html",
            recommendations=recommendations,
            city=city,
            cuisine=cuisine,
        )

    return render_template(
        "index.html",
        cities=CITIES,
        cuisines=CUISINES,
        veg_types=VEG_TYPES,
        price_ranges=PRICE_RANGES,
        occasions=OCCASIONS,
    )


@app.route("/reserve/<restaurant>", methods=["GET", "POST"])
def reserve(restaurant):
    city = request.args.get("city", "")
    cuisine = request.args.get("cuisine", "")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        date = request.form["date"]
        time = request.form["time"]
        people = request.form["people"]
        city = request.form.get("city", city)
        cuisine = request.form.get("cuisine", cuisine)

        conn = get_db_connection()
        conn.execute(
            """INSERT INTO reservations
               (id, restaurant, name, phone, date, time, people, cuisine, city)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), restaurant, name, phone, date, time, people, cuisine, city),
        )
        conn.commit()
        conn.close()

        # Implicit feedback: a real booking increases this restaurant's
        # popularity signal for future recommendations.
        if city:
            reco.bump_popularity(restaurant, city)

        flash("Reservation successful!")
        return redirect(url_for("success", restaurant=restaurant))

    return render_template("reserve.html", restaurant=restaurant, city=city, cuisine=cuisine)


@app.route("/success/<restaurant>")
def success(restaurant):
    return render_template("success.html", restaurant=restaurant)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
