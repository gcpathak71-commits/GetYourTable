"""
create_db.py
Builds restaurants.db and enriches every row with the extra attributes
the ML recommender needs: rating, price_range, veg_type, tags, popularity.

The enrichment is deterministic (seeded by restaurant name) so the dataset
is reproducible every time you re-run this script.
"""

import sqlite3
import hashlib
import random

DB_PATH = "restaurants.db"

# ---------------------------------------------------------------------------
# 1. Base dataset (name, city, cuisine, address) — same restaurants as before
# ---------------------------------------------------------------------------
restaurants = [
    # ---------- Delhi ----------
    ("Delhi Zaika", "Delhi", "North Indian", "Connaught Place,Delhi"),
    ("Saravana Bhavan", "Delhi", "South Indian", "Janpath,Delhi"),
    ("China Garden", "Delhi", "Chinese", "Chanakyapuri,Delhi"),
    ("Big Chill", "Delhi", "Italian", "Khan Market,Delhi"),
    ("Paranthe Wali Gali", "Delhi", "Street Food", "Chandni Chowk,Delhi"),
    ("Olive Bar & Kitchen", "Delhi", "Continental", "Mehrauli,Delhi"),
    ("Karim's", "Delhi", "Awadhi", "Jama Masjid,Delhi"),

    # ---------- Mumbai ----------
    ("Britannia & Co.", "Mumbai", "North Indian", "Ballard Estate,Mumbai"),
    ("Anand Bhavan", "Mumbai", "South Indian", "Matunga,Mumbai"),
    ("Mainland China", "Mumbai", "Chinese", "Andheri,Mumbai"),
    ("Trattoria", "Mumbai", "Italian", "Cuffe Parade,Mumbai"),
    ("Cannon Pav Bhaji", "Mumbai", "Street Food", "VT Station,Mumbai"),
    ("Indigo Delicatessen", "Mumbai", "Continental", "Colaba,Mumbai"),
    ("Gajalee", "Mumbai", "Seafood", "Vile Parle,Mumbai"),
    ("Bade Miya", "Mumbai", "Awadhi", "Colaba,Mumbai"),

    # ---------- Bangalore ----------
    ("Karavalli", "Bangalore", "North Indian", "Residency Road,Bangalore"),
    ("Mavalli Tiffin Room", "Bangalore", "South Indian", "Lalbagh,Bangalore"),
    ("Chung Wah", "Bangalore", "Chinese", "MG Road,Bangalore"),
    ("Little Italy", "Bangalore", "Italian", "Indiranagar,Bangalore"),
    ("VV Puram Food Street", "Bangalore", "Street Food", "VV Puram,Bangalore"),
    ("The Only Place", "Bangalore", "Continental", "Museum Road,Bangalore"),
    ("Fish Factory", "Bangalore", "Seafood", "Koramangala,Bangalore"),

    # ---------- Chennai ----------
    ("Copper Chimney", "Chennai", "North Indian", "Alwarpet,Chennai"),
    ("Murugan Idli Shop", "Chennai", "South Indian", "T Nagar,Chennai"),
    ("Cascade", "Chennai", "Chinese", "Nungambakkam,Chennai"),
    ("Little Italy", "Chennai", "Italian", "Besant Nagar,Chennai"),
    ("Marina Beach Stalls", "Chennai", "Street Food", "Marina Beach,Chennai"),
    ("Sandy's Kitchen", "Chennai", "Continental", "Wallace Garden,Chennai"),
    ("The Marina", "Chennai", "Seafood", "College Road,Chennai"),
    ("Buhari Hotel", "Chennai", "Awadhi", "Mount Road,Chennai"),

    # ---------- Kolkata ----------
    ("Arsalan", "Kolkata", "North Indian", "Park Circus,Kolkata"),
    ("Banana Leaf", "Kolkata", "South Indian", "Ballygunge,Kolkata"),
    ("Beijing", "Kolkata", "Chinese", "Tangra,Kolkata"),
    ("Casa Toscana", "Kolkata", "Italian", "Ballygunge,Kolkata"),
    ("Balwant Singh's Tea Shop", "Kolkata", "Street Food", "Bhowanipore,Kolkata"),
    ("Peter Cat", "Kolkata", "Continental", "Park Street,Kolkata"),
    ("Fish Fish", "Kolkata", "Seafood", "Hindustan Park,Kolkata"),
    ("Oudh 1590", "Kolkata", "Awadhi", "Deshapriya Park,Kolkata"),

    # ---------- Hyderabad ----------
    ("Paradise Biryani", "Hyderabad", "North Indian", "Secunderabad,Hyderabad"),
    ("Chutneys", "Hyderabad", "South Indian", "Banjara Hills,Hyderabad"),
    ("Chinese Pavilion", "Hyderabad", "Chinese", "Banjara Hills,Hyderabad"),
    ("Little Italy", "Hyderabad", "Italian", "Jubilee Hills,Hyderabad"),
    ("Ram ki Bandi", "Hyderabad", "Street Food", "Nampally,Hyderabad"),
    ("Olive Bistro", "Hyderabad", "Continental", "Gandipet,Hyderabad"),
    ("Seafood Paradise", "Hyderabad", "Seafood", "Hitech City,Hyderabad"),
    ("Shah Ghouse", "Hyderabad", "Awadhi", "Charminar,Hyderabad"),

    # ---------- Jaipur ----------
    ("Handi Restaurant", "Jaipur", "North Indian", "MI Road,Jaipur"),
    ("Dasaprakash", "Jaipur", "South Indian", "MI Road,Jaipur"),
    ("Dragon House", "Jaipur", "Chinese", "Khasa Kothi,Jaipur"),
    ("Little Italy", "Jaipur", "Italian", "C Scheme,Jaipur"),
    ("Masala Chowk", "Jaipur", "Street Food", "Ram Niwas Garden,Jaipur"),
    ("Spice Court", "Jaipur", "Continental", "Civil Lines,Jaipur"),
    ("Surya Mahal", "Jaipur", "Awadhi", "MI Road,Jaipur"),

    # ---------- Pune ----------
    ("Vaishali", "Pune", "North Indian", "Fergusson College Road,Pune"),
    ("Wadeshwar", "Pune", "South Indian", "JM Road,Pune"),
    ("Mainland China", "Pune", "Chinese", "Bund Garden Road,Pune"),
    ("Dario's", "Pune", "Italian", "Koregaon Park,Pune"),
    ("Garden Vada Pav", "Pune", "Street Food", "Camp,Pune"),
    ("Arthur's Theme", "Pune", "Continental", "Koregaon Park,Pune"),
    ("Fish Curry Rice", "Pune", "Seafood", "Tilak Road,Pune"),
    ("Blue Nile", "Pune", "Awadhi", "Bund Garden,Pune"),

    # ---------- Ahmedabad ----------
    ("Agashiye", "Ahmedabad", "North Indian", "Lal Darwaja,Ahmedabad"),
    ("Dakshinayan", "Ahmedabad", "South Indian", "Navrangpura,Ahmedabad"),
    ("China House", "Ahmedabad", "Chinese", "Vastrapur,Ahmedabad"),
    ("La Pino'z Pizza", "Ahmedabad", "Italian", "Navrangpura,Ahmedabad"),
    ("Manek Chowk", "Ahmedabad", "Street Food", "Old City,Ahmedabad"),
    ("Tomato's", "Ahmedabad", "Continental", "CG Road,Ahmedabad"),
    ("Mirch Masala", "Ahmedabad", "Awadhi", "SG Highway,Ahmedabad"),

    # ---------- Lucknow ----------
    ("Tunday Kababi", "Lucknow", "North Indian", "Aminabad,Lucknow"),
    ("Udupi Sagar", "Lucknow", "South Indian", "Hazratganj,Lucknow"),
    ("Mainland China", "Lucknow", "Chinese", "Gomti Nagar,Lucknow"),
    ("Cappuccino Blast", "Lucknow", "Italian", "Mall Avenue,Lucknow"),
    ("Royal Cafe", "Lucknow", "Street Food", "Hazratganj,Lucknow"),
    ("Falaknuma", "Lucknow", "Continental", "Hazratganj,Lucknow"),
    ("Dastarkhwan", "Lucknow", "Awadhi", "Lalbagh,Lucknow"),

    # ---------- Chandigarh ----------
    ("Swagath Restaurant", "Chandigarh", "North Indian", "Sector 26,Chandigarh"),
    ("Sankalp", "Chandigarh", "South Indian", "Sector 26,Chandigarh"),
    ("Yo! China", "Chandigarh", "Chinese", "Sector 17,Chandigarh"),
    ("Virgin Courtyard", "Chandigarh", "Italian", "Sector 7,Chandigarh"),
    ("Night Food Street", "Chandigarh", "Street Food", "Sector 14,Chandigarh"),
    ("Backpackers Cafe", "Chandigarh", "Continental", "Sector 9,Chandigarh"),
    ("Baba Chicken", "Chandigarh", "Awadhi", "Sector 14,Chandigarh"),

    # ---------- Goa ----------
    ("Vinayak Family Restaurant", "Goa", "North Indian", "Assagao,Goa"),
    ("Anand Ashram", "Goa", "South Indian", "Mapusa,Goa"),
    ("Go With The Flow", "Goa", "Chinese", "Baga,Goa"),
    ("Thalassa", "Goa", "Italian", "Siolim,Goa"),
    ("Miramar Beach Stalls", "Goa", "Street Food", "Miramar,Goa"),
    ("Gunpowder", "Goa", "Continental", "Assagao,Goa"),
    ("Ritz Classic", "Goa", "Seafood", "Panjim,Goa"),
    ("Mum's Kitchen", "Goa", "Awadhi", "Miramar,Goa"),

    # ---------- Indore ----------
    ("Nafees Restaurant", "Indore", "North Indian", "Old Palasia,Indore"),
    ("Sagar Gaire", "Indore", "South Indian", "Vijay Nagar,Indore"),
    ("Chinese Hut", "Indore", "Chinese", "Sarafa,Indore"),
    ("Oregano", "Indore", "Italian", "Sayaji Hotel,Indore"),
    ("Sarafa Bazaar", "Indore", "Street Food", "Sarafa,Indore"),
    ("Mediterra", "Indore", "Continental", "Sayaji Hotel,Indore"),
    ("Shree Gurukripa", "Indore", "Awadhi", "Sarwate,Indore"),

    # ---------- Bhopal ----------
    ("Manohar Dairy", "Bhopal", "North Indian", "Hamidia Road,Bhopal"),
    ("Krishna Restaurant", "Bhopal", "South Indian", "MP Nagar,Bhopal"),
    ("Chinese Hut", "Bhopal", "Chinese", "New Market,Bhopal"),
    ("La Kuchina", "Bhopal", "Italian", "Jehangirabad,Bhopal"),
    ("Chatori Gali", "Bhopal", "Street Food", "Peer Gate,Bhopal"),
    ("Under The Mango Tree", "Bhopal", "Continental", "Shyamla Hills,Bhopal"),
    ("Za-Aiqa", "Bhopal", "Awadhi", "Peer Gate,Bhopal"),

    # ---------- Surat ----------
    ("Gopal Locho Khaman", "Surat", "North Indian", "Athwa,Surat"),
    ("Woodland Restaurant", "Surat", "South Indian", "Nanpura,Surat"),
    ("Wok On Fire", "Surat", "Chinese", "Athwalines,Surat"),
    ("La Pino'z Pizza", "Surat", "Italian", "Ghod Dod Road,Surat"),
    ("Surti Locho Stalls", "Surat", "Street Food", "Athwa,Surat"),
    ("The Lime Tree", "Surat", "Continental", "Athwalines,Surat"),
    ("Sea Salt", "Surat", "Seafood", "Adajan,Surat"),

    # ---------- Shimla ----------
    ("Baljees", "Shimla", "North Indian", "Mall Road,Shimla"),
    ("Sagar Ratna", "Shimla", "South Indian", "The Mall,Shimla"),
    ("Chopsticks", "Shimla", "Chinese", "Lakkar Bazar,Shimla"),
    ("Cafe Sol", "Shimla", "Italian", "Hotel Combermere,Shimla"),
    ("Lakkar Bazar Stalls", "Shimla", "Street Food", "Lakkar Bazar,Shimla"),
    ("Ashiana & Goofa", "Shimla", "Continental", "The Ridge,Shimla"),
    ("Baljee's", "Shimla", "Awadhi", "Mall Road,Shimla"),

    # ---------- Ranchi ----------
    ("Kaveri Restaurant", "Ranchi", "North Indian", "Main Road,Ranchi"),
    ("Anand Restaurant", "Ranchi", "South Indian", "Lalpur,Ranchi"),
    ("Yo! China", "Ranchi", "Chinese", "Circular Road,Ranchi"),
    ("Little Italy", "Ranchi", "Italian", "Main Road,Ranchi"),
    ("Firayalal Chowk", "Ranchi", "Street Food", "Firayalal Chowk,Ranchi"),
    ("Capitol Residency", "Ranchi", "Continental", "Station Road,Ranchi"),
    ("Punjab Sweet House", "Ranchi", "Awadhi", "Upper Bazaar,Ranchi"),
]

# ---------------------------------------------------------------------------
# 2. Feature vocabulary used to deterministically enrich every restaurant.
#    Each restaurant gets a reproducible "fingerprint" derived from its name,
#    so re-running this script always yields the same enriched dataset --
#    important for reproducible ML experiments.
# ---------------------------------------------------------------------------
PRICE_RANGES = ["Budget", "Mid-Range", "Premium"]
PRICE_DISPLAY = {
    "Budget": "\u20b9200 - \u20b9500 per person",
    "Mid-Range": "\u20b9500 - \u20b91000 per person",
    "Premium": "\u20b91000+ per person",
}
VEG_TYPES = ["Veg", "Non-Veg", "Both"]
TAG_POOL = [
    "romantic", "family-friendly", "rooftop", "budget-friendly", "fine-dining",
    "quick-bite", "outdoor-seating", "live-music", "buffet", "late-night",
    "pet-friendly", "kid-friendly", "scenic-view", "cozy", "trendy",
]


def _seeded_rng(name: str) -> random.Random:
    """Deterministic per-restaurant RNG so results are reproducible."""
    seed = int(hashlib.md5(name.encode()).hexdigest(), 16) % (2 ** 32)
    return random.Random(seed)


def enrich(name: str, cuisine: str):
    rng = _seeded_rng(name)
    rating = round(rng.uniform(3.2, 4.9), 1)
    price_range = rng.choice(PRICE_RANGES)
    veg_type = rng.choice(VEG_TYPES)
    tags = rng.sample(TAG_POOL, k=3)
    return rating, price_range, veg_type, ",".join(tags)


def build_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS restaurants")
    cursor.execute("""
        CREATE TABLE restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            address TEXT NOT NULL,
            rating REAL NOT NULL,
            price_range TEXT NOT NULL,
            price_display TEXT NOT NULL,
            veg_type TEXT NOT NULL,
            tags TEXT NOT NULL,
            popularity INTEGER NOT NULL DEFAULT 0
        )
    """)

    rows = []
    for name, city, cuisine, address in restaurants:
        rating, price_range, veg_type, tags = enrich(name, cuisine)
        price_display = PRICE_DISPLAY[price_range]
        rows.append((name, city, cuisine, address, rating, price_range, price_display, veg_type, tags, 0))

    cursor.executemany("""
        INSERT INTO restaurants
        (name, city, cuisine, address, rating, price_range, price_display, veg_type, tags, popularity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()
    print(f"Database created successfully with {len(rows)} ML-enriched restaurants")


if __name__ == "__main__":
    build_database()
