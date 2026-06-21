# Academic Policy Chatbot

An AI-powered chatbot that answers university academic policy questions using Retrieval-Augmented Generation (RAG).

## Problem Statement
Students struggle to find answers to academic policy questions quickly. This chatbot provides instant, accurate answers based on official university policies using RAG pipeline.

## Live Demo
Running locally at: http://127.0.0.1:5000

## Architecture
```
User Question
     ↓
Flask Backend (/chat endpoint)
     ↓
Sentence Transformer (all-MiniLM-L6-v2) — Embedding
     ↓
Vector Similarity Search (index.pkl) — Retrieval
     ↓
Top-3 Relevant Policy Chunks Retrieved
     ↓
Groq LLM (llama-3.3-70b-versatile) — Generation
     ↓
Answer + Sources returned to User
```

## Tech Stack
| Layer | Technology |
|-------|-----------|
| LLM | Groq — llama-3.3-70b-versatile |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | Pickle-based index |
| Backend | Flask (Python) |
| Frontend | HTML, CSS, JavaScript |
| RAG | Custom implementation |

## Features
- Natural language Q&A on university policies
- RAG pipeline for accurate, grounded answers
- Source citations shown with every answer
- Voice input support
- 90% pass rate on 20 test questions
- Prompt engineering with v1/v2 system prompts and few-shot examples

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/academic-chatbot.git
cd academic-chatbot
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

### 5. Build the index
```bash
python scripts/build_index.py
```

### 6. Run the app
```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project Structure
```
academic-chatbot/
├── app.py                   # Main Flask application
├── scripts/
│   └── build_index.py       # Index builder script
├── data/
│   └── policies.jsonl       # University policy data
├── storage/
│   └── index.pkl            # Vector index
├── templates/
│   └── index.html           # Frontend UI
├── static/                  # CSS and JS files
├── prompts/                 # Prompt templates
│   ├── system_prompt_v1.txt
│   ├── system_prompt_v2.txt
│   └── few_shot_examples.txt
├── tests/
│   └── test_questions.py    # 20 test questions
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Evaluation Results
| Metric | Result |
|--------|--------|
| Total test questions | 20 |
| Passed | 18 |
| Failed | 2 |
| Pass rate | 90% |
| Avg latency | ~900ms |

## Prompt Engineering
- System prompt v1 and v2 with role definition
- Few-shot examples for better responses
- Context injection from retrieved policy chunks
- Fallback handling for out-of-scope questions

## Data Format
Policies stored in `data/policies.jsonl` as JSON Lines with fields:
`id`, `title`, `text`, and `tags`. Replace with real policy documents and re-run `build_index.py`.

## Limitations
- Only answers based on indexed policy documents
- Cannot answer questions outside the policy database
- Requires internet connection for Groq API

## Team
- Student Name: Mahnoor wasif    and  Aqsa abbas
- Course: AI-Driven Software Development — 6th Semester