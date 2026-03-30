Academic Policy Chatbot (Offline RAG)
=====================================

This project is a local, offline retrieval-augmented chatbot. It answers questions
by searching a set of university policy documents and returning the most relevant
policy excerpts. The current dataset is synthetic and meant only as a demo.

Quickstart
----------
1) Create and activate a virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`

2) Install dependencies (only Flask):
   - `pip install -r requirements.txt`

3) Build the search index:
   - `python scripts/build_index.py`

4) Run the web app:
   - `python app.py`

Open `http://127.0.0.1:5000` in your browser.

Data format
-----------
Policies are stored in `data/policies.jsonl` as JSON Lines with fields:
`id`, `title`, `text`, and `tags`. Replace the synthetic file with real policy
documents and re-run the index build script.

Notes
-----
- This is a retrieval-first chatbot. It does not call external APIs or external models.
- If you want a local LLM for generative responses, you can add one later and
  use the retrieved excerpts as context.
