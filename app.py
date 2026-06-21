import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from flask import Flask, render_template, request, jsonify

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None
    util = None

# Paths
INDEX_PATH = Path("storage/index.pkl")
PROMPTS_DIR = Path("prompts")
SYSTEM_PROMPT_V1_PATH = PROMPTS_DIR / "system_prompt_v1.txt"
SYSTEM_PROMPT_V2_PATH = PROMPTS_DIR / "system_prompt_v2.txt"
FEW_SHOT_EXAMPLES_PATH = PROMPTS_DIR / "few_shot_examples.txt"

app = Flask(__name__)

# Global variables
INDEX = None
MODEL = None
SYSTEM_PROMPT_V1 = None
SYSTEM_PROMPT_V2 = None
FEW_SHOT_EXAMPLES = None

def generate_llm_answer(context, question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an academic assistant. Answer only using the given context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    )
    return response.choices[0].message.content

def load_prompt_file(path, fallback_text=""):
    """Load a prompt template from disk and fall back safely if needed."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = handle.read().strip()
        if loaded:
            return loaded
    except FileNotFoundError:
        print(f"⚠️ Warning: {path} not found. Using fallback text.")
    except Exception as exc:
        print(f"⚠️ Warning: Could not read {path}. Error: {exc}")
    return fallback_text


def load_prompt_assets():
    """Load prompt templates used for prompt engineering."""
    global SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2, FEW_SHOT_EXAMPLES

    SYSTEM_PROMPT_V1 = load_prompt_file(
        SYSTEM_PROMPT_V1_PATH,
        "You are A Professional University Academic Policy Assistant. Use only the retrieved context."
    )
    SYSTEM_PROMPT_V2 = load_prompt_file(
        SYSTEM_PROMPT_V2_PATH,
        "You are A Professional University Academic Policy Assistant. Answer using only the retrieved context."
    )
    FEW_SHOT_EXAMPLES = load_prompt_file(
        FEW_SHOT_EXAMPLES_PATH,
        "No examples available."
    )


def build_prompt(user_question, retrieved_context, policy_title):
    """Build the final prompt by injecting retrieved context and placeholders."""
    base_prompt = SYSTEM_PROMPT_V2 or SYSTEM_PROMPT_V1 or ""
    examples = FEW_SHOT_EXAMPLES or ""

    prompt = base_prompt.format(
        user_question=user_question,
        retrieved_context=retrieved_context,
        policy_title=policy_title,
    )

    if examples and examples != "No examples available.":
        prompt = f"{prompt}\n\nFew-shot Examples:\n{examples}"

    return prompt


def generate_answer_from_context(user_question, retrieved_context, policy_title):
    """Generate a structured answer using the retrieved context."""
    context = (retrieved_context or "").strip()

    if not context:
        return {
            "answer": (
                "Answer:\n"
                "The policy was not found in the retrieved context.\n\n"
                "Source:\nPolicy not found\n\n"
                "Confidence:\nLow"
            ),
            "source": "Policy not found",
            "confidence": "Low",
        }

    # Keep the response concise and grounded in the retrieved policy text.
    first_sentence = context.split(".")[0].strip()
    if not first_sentence.endswith("."):
        first_sentence = f"{first_sentence}."

    answer_text = first_sentence
    if len(context.split()) > 30:
        answer_text = context.split(".")[0].strip()

    if answer_text.lower().startswith("the policy"):
        answer_text = answer_text
    else:
        answer_text = f"According to the retrieved policy, {answer_text}"

    confidence = "High" if len(context.split()) >= 12 else "Medium"

    return {
        "answer": (
            f"Answer:\n{answer_text}\n\n"
            f"Source:\n{policy_title}\n\n"
            f"Confidence:\n{confidence}"
        ),
        "source": policy_title,
        "confidence": confidence,
    }


def load_resources():
    """Load the index and model used by the application."""
    global INDEX, MODEL

    load_prompt_assets()

    # 1. Load the Index
    if INDEX_PATH.exists():
        with INDEX_PATH.open("rb") as handle:
            INDEX = pickle.load(handle)
        print("✅ Index loaded successfully.")
    else:
        print("❌ Error: storage/index.pkl not found. Run build_index.py first!")

    # 2. Load the AI Model (if available)
    if SentenceTransformer is None or util is None:
        print(
            "⚠️ Warning: sentence-transformers is not available. "
            "The app will run in fallback mode."
        )
        return

    print("⏳ Loading AI Model (all-MiniLM-L6-v2)...")
    MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model ready!")


def answer_query(query, index, top_k=3):
    """Retrieve policy chunks, build a final prompt, and generate a structured answer."""
    docs = index.get("docs", [])

    if MODEL is None or util is None:
        return (
            "System is not ready. Please install the required dependencies and run build_index.py.",
            [],
        )

    if not docs:
        return (
            "Answer:\nThe policy index is empty.\n\nSource:\nPolicy not found\n\nConfidence:\nLow",
            [],
        )

    if SYSTEM_PROMPT_V2 is None or SYSTEM_PROMPT_V1 is None:
        load_prompt_assets()

    # Step 1: Retrieve relevant policy chunks using semantic similarity.
    doc_embeddings = index.get("doc_embeddings")
    if doc_embeddings is None:
        return (
            "Answer:\nThe policy index is missing embeddings.\n\nSource:\nPolicy not found\n\nConfidence:\nLow",
            [],
        )

    query_embedding = MODEL.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, doc_embeddings)[0]

    results = []
    seen_texts = set()
    for i, doc in enumerate(docs):
        score = cosine_scores[i].item()
        text_content = doc.get("text", "").strip()
        if score > 0.35 and text_content and text_content not in seen_texts:
            results.append(
                {
                    "id": doc.get("id"),
                    "title": doc.get("title", "Unknown Policy"),
                    "score": score,
                    "text": text_content,
                }
            )
            seen_texts.add(text_content)

    results = sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]

    # Step 2: Check if any results were retrieved.
    if not results:
        return (
            "Answer:\nThe policy was not found in the retrieved context.\n\n"
            "Source:\nPolicy not found\n\n"
            "Confidence:\nLow",
            [],
        )

    # Build context for Claude
    context_text = "\n\n".join(
        f"{item['title']}: {item['text']}"
        for item in results
    )

    # Call Anthropic Claude model
    answer_text = generate_llm_answer(context_text, query)

    return answer_text, results


@app.route("/")
def home():
    return render_template("index.html")


# app.py mein /chat route update karo

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"answer": "Please enter a question.", "sources": []})

    if INDEX is None:
        return jsonify({"answer": "System not ready.", "sources": []})

    # Agent use karo instead of direct answer_query
    from agent import run_agent
    answer, iterations = run_agent(message, INDEX, MODEL, util, client)
    
    return jsonify({
        "answer": answer,
        "sources": [],
        "agent_iterations": iterations  # bonus: show how many steps agent took
    })

if __name__ == "__main__":
    load_resources()
    app.run(host="127.0.0.1", port=5000, debug=False)