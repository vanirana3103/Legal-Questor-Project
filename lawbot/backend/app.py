"""
LawBot Backend - Flask + RAG + Groq LLM
LegalQuestor Final Year Project
"""

from flask import Flask, request, jsonify, send_from_directory
import json, pickle, os, requests
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__, static_folder='../../', static_url_path='')
# ── Load RAG index ──────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)

with open(os.path.join(BASE, 'chunks.json')) as f:
    CHUNKS = json.load(f)

with open(os.path.join(BASE, 'vectorizer.pkl'), 'rb') as f:
    VECTORIZER = pickle.load(f)

with open(os.path.join(BASE, 'matrix.pkl'), 'rb') as f:
    MATRIX = pickle.load(f)

print(f"✅ Loaded {len(CHUNKS)} legal chunks from IPC, BNS, CrPC, PWDVA")

# ── RAG retrieval ───────────────────────────────────────────────────────────
def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Find the most relevant legal text chunks for a query."""
    q_vec = VECTORIZER.transform([query])
    scores = cosine_similarity(q_vec, MATRIX).flatten()
    top_indices = scores.argsort()[-top_k:][::-1]
    results = []
    for idx in top_indices:
        if scores[idx] > 0.01:
            results.append({
                'source': CHUNKS[idx]['source'],
                'text': CHUNKS[idx]['text'],
                'score': float(scores[idx])
            })
    return results

# ── Groq LLM call ───────────────────────────────────────────────────────────
# ── Groq LLM call ───────────────────────────────────────────────────────────
def call_groq(api_key: str, messages: list) -> str:
    """Call Groq API with conversation + legal context."""
    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            # UPDATED: Changed from 'llama3-8b-8192' to the supported 'llama-3.1-8b-instant'
            'model': 'llama-3.1-8b-instant', 
            'messages': messages,
            'max_tokens': 1024,
            'temperature': 0.4
        },
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"Groq API error {response.status_code}: {response.text}")
    return response.json()['choices'][0]['message']['content']
# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are LawBot, an AI-powered legal assistant for LegalQuestor — a platform that helps crime victims in India understand their legal rights.

You have access to the Indian Penal Code (IPC), Bharatiya Nyaya Sanhita (BNS), Code of Criminal Procedure (CrPC), and the Protection of Women from Domestic Violence Act (PWDVA).

Your personality:
- Speak with empathy, clarity, and warmth. Many users are in distress.
- Avoid complex legal jargon. Explain in simple, easy-to-understand language.
- Be supportive and encouraging.
- Always cite which law/section you're referring to.
- If someone describes a crime, identify relevant sections and explain their rights.
- Guide users step-by-step on how to file an FIR or get protection orders when needed.
- NEVER give false legal advice. If unsure, say so and recommend consulting a lawyer.
- You can help with: understanding crimes & punishments, FIR filing, domestic violence, cyber crimes, theft, harassment, women's rights, and more.

Always end responses about serious matters with: "Remember, you can also consult a free legal aid center near you."
"""

# ── API Routes ───────────────────────────────────────────────────────────────

# ── API Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    # This serves your main landing page (the one in the first screenshot)
    return send_from_directory('../../legalquestor', 'index.html')

@app.route('/chatbot.html')
def chatbot_page():
    # This serves your LawBot chat page
    return send_from_directory('../frontend', 'index.html')

@app.route('/documents.html')
def documents_page():
    # This serves your Generate Documents page
    return send_from_directory('../../legalquestor', 'documents.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # ✅ Get API key from backend (.env)
        api_key = os.getenv("GROQ_API_KEY")
        print("DEBUG API KEY:", api_key)

        if not api_key:
            return jsonify({'error': 'Server configuration error: API key missing'}), 500

        # Step 1: Retrieve relevant legal context (RAG)
        retrieved = retrieve(user_message, top_k=5)
        
        context_text = ""
        sources_used = []

        if retrieved:
            context_text = "\n\n--- RELEVANT LEGAL PROVISIONS ---\n"
            for r in retrieved:
                context_text += f"\n[{r['source']}]: {r['text']}\n"
                if r['source'] not in sources_used:
                    sources_used.append(r['source'])

        # Step 2: Build messages for Groq
        system_with_context = SYSTEM_PROMPT

        if context_text:
            system_with_context += f"\n\nUse the following retrieved legal provisions to answer accurately:{context_text}"

        messages = [{'role': 'system', 'content': system_with_context}]

        # Add conversation history
        for msg in history[-6:]:
            messages.append(msg)

        messages.append({'role': 'user', 'content': user_message})

        # Step 3: Call Groq
        reply = call_groq(api_key, messages)

        return jsonify({
            'reply': reply,
            'sources': sources_used,
            'chunks_retrieved': len(retrieved)
        })

    except Exception as e:
        error_msg = str(e)
        print("ERROR:", error_msg)

        if '401' in error_msg or 'Invalid API Key' in error_msg:
            return jsonify({'error': 'Invalid Groq API key'}), 401

        return jsonify({'error': f'Something went wrong: {error_msg}'}), 500
    
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'chunks_loaded': len(CHUNKS),
        'sources': ['IPC', 'BNS', 'CrPC', 'PWDVA']
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Test RAG retrieval directly."""
    data = request.json
    query = data.get('query', '')
    results = retrieve(query, top_k=3)
    return jsonify({'results': results})

# ── CORS headers (so frontend JS can call this) ──────────────────────────────
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/api/chat', methods=['OPTIONS'])
def chat_options():
    return '', 204

if __name__ == '__main__':
    print("\n🚀 LawBot Backend Starting...")
    print("📚 Legal corpus: IPC | BNS | CrPC | PWDVA")
    print("🌐 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
