# Get Your Table — AI/ML Edition

Live demo: https:https://get-your-table.vercel.app/



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
