# Get Your Table — AI/ML Edition

Live demo: https:https://get-your-table.vercel.app/

An upgraded version of the original "Get Your Table" project. The old
recommender just did `random.choice()` over restaurants that matched the
city + cuisine filters. This version replaces that with a real, explainable
machine-learning recommendation pipeline:

## What changed

1. **Richer data** — every restaurant now also has a `rating`, `price_range`
   (`$`/`$$`/`$$$`), `veg_type`, and descriptive `tags` (romantic, rooftop,
   budget-friendly, etc.), plus a `popularity` counter.
2. **Content-based filtering** — restaurant profiles and the user's request
   are vectorized with TF-IDF (`scikit-learn`), and ranked by cosine
   similarity.
3. **Weighted scoring** — final ranking blends similarity (55%), normalized
   rating (30%), and normalized popularity (15%) into one `match_score`.
4. **Lightweight collaborative filtering** — if a phone number is supplied,
   the app checks the user's past reservations and boosts restaurants that
   share a cuisine with what they've booked before.
5. **Feedback loop** — every confirmed reservation increments that
   restaurant's `popularity`, so the model's rankings adapt over time based
   on real bookings.
6. **UI** — the results page now shows the top 3 ranked matches with a
   match-score badge instead of a single random pick.

## Project structure

```
get-your-table-ai/
├── app.py                  # Flask routes
├── recommendor.py          # ML recommender (TF-IDF + cosine similarity)
├── create_db.py            # Builds restaurants.db with ML features
├── create_reservations.py  # Builds reservations table
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── recommend.html
│   ├── reserve.html
│   └── success.html
└── static/
    └── style.css
```

## Running it in VS Code

1. Open this folder in VS Code.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Build the database (run once, or again any time you want to reset it):
   ```bash
   python create_db.py
   python create_reservations.py
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Where to take this further

- Swap TF-IDF for sentence-embedding similarity (e.g. `sentence-transformers`)
  for semantic matching instead of keyword overlap.
- Replace the heuristic collaborative-filtering boost with real matrix
  factorization (e.g. `surprise` or `implicit`) once you have enough
  reservation history.
- Add a `/api/recommend` JSON endpoint so a mobile app or chatbot front-end
  can call the recommender directly.
