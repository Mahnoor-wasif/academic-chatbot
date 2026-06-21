# tools.py - naya file banao

def tool_rag_search(query, index, model, util):
    """Tool 1: Search policy documents using semantic search"""
    docs = index.get("docs", [])
    doc_embeddings = index.get("doc_embeddings")
    query_embedding = model.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, doc_embeddings)[0]
    
    results = []
    for i, doc in enumerate(docs):
        if scores[i].item() > 0.35:
            results.append({
                "title": doc.get("title", "Unknown"),
                "text": doc.get("text", ""),
                "score": scores[i].item()
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)[:3]


def tool_get_policy_by_title(title, index):
    """Tool 2: Get exact policy by matching title"""
    docs = index.get("docs", [])
    for doc in docs:
        if title.lower() in doc.get("title", "").lower():
            return {"title": doc["title"], "text": doc["text"]}
    return {"error": f"Policy '{title}' not found"}


def tool_summarise_text(text):
    """Tool 3: Summarise long policy text"""
    sentences = text.split(".")
    short = ". ".join(sentences[:3])
    return short + "." if short else text