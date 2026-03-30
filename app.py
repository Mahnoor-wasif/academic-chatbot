import pickle
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from sentence_transformers import SentenceTransformer, util

# Paths
INDEX_PATH = Path("storage/index.pkl")

app = Flask(__name__)

# Global variables
INDEX = None
MODEL = None

def load_resources():
    """AI Model aur saved index ko load karne ke liye"""
    global INDEX, MODEL
    
    # 1. Load the Index
    if INDEX_PATH.exists():
        with open(INDEX_PATH, "rb") as handle:
            INDEX = pickle.load(handle)
        print("✅ Index loaded successfully.")
    else:
        print("❌ Error: storage/index.pkl not found. Run build_index.py first!")

    # 2. Load the AI Model
    print("⏳ Loading AI Model (all-MiniLM-L6-v2)...")
    MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model ready!")

def answer_query(query, index, top_k=3):
    docs = index["docs"]
    doc_embeddings = index["doc_embeddings"]
    
    # 1. User query ko vector mein badlein
    query_embedding = MODEL.encode(query, convert_to_tensor=True)
    
    # 2. Cosine Similarity calculate karein
    cosine_scores = util.cos_sim(query_embedding, doc_embeddings)[0]
    
    # 3. Results filter karein (Duplicate check ke saath)
    results = []
    seen_texts = set()  # Duplicates ko rokne ke liye

    for i in range(len(docs)):
        score = cosine_scores[i].item()
        text_content = docs[i]["text"].strip()
        
        # 0.35 threshold aur uniqueness check
        if score > 0.35 and text_content not in seen_texts:
            results.append({
                "id": docs[i]["id"],
                "title": docs[i]["title"],
                "score": score,
                "text": text_content
            })
            seen_texts.add(text_content)
    
    # Sabse behtar top results ko sort karein
    results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
    
    if not results:
        return "I'm sorry, I couldn't find a policy that matches your question. Could you rephrase?", []

    # 4. Final response build karein (No red pins, No repeats)
    response_lines = ["Based on the academic policies, here is what I found:\n"]
    for item in results:
        response_lines.append(f"**{item['title']}**")
        response_lines.append(f"{item['text']}\n")
    
    return "\n".join(response_lines), results

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"answer": "Please enter a question.", "sources": []})

    if INDEX is None:
        return jsonify({"answer": "System is not ready. Please run build_index.py.", "sources": []})

    answer, sources = answer_query(message, INDEX)
    return jsonify({"answer": answer, "sources": sources})

if __name__ == "__main__":
    load_resources()
    app.run(host="127.0.0.1", port=5000, debug=True)