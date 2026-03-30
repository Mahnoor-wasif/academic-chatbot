import json
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Paths
DATA_PATH = Path("data/policies.jsonl")
OUTPUT_PATH = Path("storage/index.pkl")

def load_documents(path):
    documents = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            documents.append(json.loads(line))
    return documents

def main():
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing dataset: {DATA_PATH}")

    # 1. Documents load karein
    documents = load_documents(DATA_PATH)
    if not documents:
        raise SystemExit("No policy documents found.")

    # 2. AI Model load karein (all-MiniLM-L6-v2 chota aur fast model hai)
    print("Loading AI Model (Sentence-Transformers)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 3. Har policy ka text prepare karein embedding ke liye
    # Hum title aur text dono ko combine kar rahe hain behtar result ke liye
    policy_texts = [f"{doc['title']}: {doc['text']}" for doc in documents]

    # 4. Generate Embeddings (AI magic happens here)
    print(f"Generating embeddings for {len(documents)} documents...")
    doc_embeddings = model.encode(policy_texts, show_progress_bar=True)

    # 5. Index file save karein
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("wb") as handle:
        pickle.dump(
            {
                "docs": documents,
                "doc_embeddings": doc_embeddings,
                "model_name": 'all-MiniLM-L6-v2'
            },
            handle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    print(f"Success! Wrote AI index to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()