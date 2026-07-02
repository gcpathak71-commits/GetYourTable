"""
recommendor.py
--------------
An ML-powered replacement for the old "random.choice()" recommender.

Techniques used:
1. Content-based filtering
   Every restaurant is turned into a text "profile" (cuisine + veg type +
   price range + descriptive tags). A TF-IDF vectorizer converts these
   profiles into vectors, and cosine similarity scores how well a
   restaurant matches what the user asked for.

2. Weighted ranking
   final_score = 0.55 * content_similarity
               + 0.30 * normalized_rating
               + 0.15 * normalized_popularity

3. Lightweight collaborative filtering
   If the user has booked before (looked up by phone number in the
   `reservations` table), restaurants sharing a cuisine with their past
   bookings get a small score boost -- a simple, explainable stand-in
   for a full collaborative-filtering model.

Everything runs locally with scikit-learn; no external API calls needed.
"""

import sqlite3
from typing import List, Dict, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = "restaurants.db"


class ContentRecommender:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _profile_text(self, row: sqlite3.Row) -> str:
        """Build the text 'document' fed into the TF-IDF vectorizer.
        Cuisine is repeated to weight it more heavily than the other
        attributes, since it is usually the strongest match signal."""
        return " ".join([
            row["cuisine"], row["cuisine"], row["cuisine"],
            row["veg_type"],
            row["price_range"],
            row["tags"].replace(",", " "),
        ])

    def _past_cuisines(self, phone: Optional[str]) -> set:
        """Look up cuisines the user has booked before, for a simple
        collaborative-filtering style boost."""
        if not phone:
            return set()
        cur = self.conn.cursor()
        cur.execute(
            "SELECT DISTINCT cuisine FROM reservations WHERE phone = ? AND cuisine IS NOT NULL",
            (phone,),
        )
        return {r[0] for r in cur.fetchall() if r[0]}

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def recommend(
        self,
        city: str,
        cuisine: str,
        veg_type: Optional[str] = None,
        price_range: Optional[str] = None,
        occasion: Optional[str] = None,
        phone: Optional[str] = None,
        top_n: int = 3,
    ) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM restaurants WHERE city = ?", (city,))
        rows = cur.fetchall()
        if not rows:
            return []

        documents = [self._profile_text(r) for r in rows]

        query_parts = [cuisine, cuisine, cuisine]
        if veg_type:
            query_parts.append(veg_type)
        if price_range:
            query_parts.append(price_range)
        if occasion:
            query_parts.append(occasion)
        query_text = " ".join(query_parts)

        # --- Content-based similarity (TF-IDF + cosine similarity) ---
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents + [query_text])
        restaurant_vectors = tfidf_matrix[:-1]
        query_vector = tfidf_matrix[-1]
        similarities = cosine_similarity(query_vector, restaurant_vectors)[0]

        ratings = [r["rating"] for r in rows]
        popularities = [r["popularity"] for r in rows]
        max_rating = max(ratings) or 1
        max_pop = max(popularities) or 1

        past_cuisines = self._past_cuisines(phone)

        scored = []
        for row, sim, rating, pop in zip(rows, similarities, ratings, popularities):
            norm_rating = rating / max_rating
            norm_pop = pop / max_pop if max_pop else 0
            score = 0.55 * sim + 0.30 * norm_rating + 0.15 * norm_pop

            # Collaborative-filtering style boost: user has liked this cuisine before
            if row["cuisine"] in past_cuisines:
                score += 0.10

            scored.append({
                "name": row["name"],
                "address": row["address"],
                "cuisine": row["cuisine"],
                "rating": rating,
                "price_range": row["price_range"],
                "price_display": row["price_display"],
                "veg_type": row["veg_type"],
                "tags": row["tags"].split(","),
                "match_score": round(float(min(score, 1.0)) * 100, 1),  # as a %
            })

        # Restaurants that exactly match the requested cuisine are ranked
        # first (still ordered by score within that group), then the rest
        # act as "you might also like" cross-cuisine suggestions.
        exact = [s for s in scored if s["cuisine"] == cuisine]
        other = [s for s in scored if s["cuisine"] != cuisine]
        exact.sort(key=lambda x: x["match_score"], reverse=True)
        other.sort(key=lambda x: x["match_score"], reverse=True)

        results = (exact + other)[:top_n]
        return results

    def bump_popularity(self, restaurant_name: str, city: str) -> None:
        """Called after a successful reservation so future recommendations
        reflect real demand (a simple implicit-feedback signal)."""
        self.conn.execute(
            "UPDATE restaurants SET popularity = popularity + 1 WHERE name = ? AND city = ?",
            (restaurant_name, city),
        )
        self.conn.commit()
