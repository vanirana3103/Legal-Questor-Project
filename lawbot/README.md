# ⚖️ LawBot — LegalQuestor AI Chatbot

An AI-powered legal chatbot using **RAG (Retrieval-Augmented Generation)** over Indian legal documents:
- 📕 Indian Penal Code (IPC)
- 📙 Bharatiya Nyaya Sanhita (BNS)
- 📘 Code of Criminal Procedure (CrPC)
- 📗 Protection of Women from Domestic Violence Act (PWDVA)

---

## 📁 Project Structure

```
lawbot/
├── backend/
│   ├── app.py            ← Flask API server
│   ├── chunks.json       ← Generated after setup
│   ├── vectorizer.pkl    ← Generated after setup
│   └── matrix.pkl        ← Generated after setup
├── frontend/
│   └── index.html        ← Standalone chatbot UI
├── legal_docs/
│   ├── IPC.pdf
│   ├── BNS.pdf
│   ├── CrPC.pdf
│   └── PWDVA.pdf
├── setup_index.py        ← Run once to build index
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup (Step-by-Step)

### Step 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Build the legal document index (run only ONCE)
```bash
python setup_index.py
```
This reads all PDFs and creates the search index files in `backend/`.

### Step 3 — Get a FREE Groq API Key
1. Go to → https://console.groq.com
2. Sign up (free, no credit card needed)
3. Click **"API Keys"** → **"Create API Key"**
4. Copy the key (starts with `gsk_...`)

### Step 4 — Start the chatbot server
```bash
python backend/app.py
```
Server runs at: **http://localhost:5000**

### Step 5 — Open the chatbot
Open your browser → **http://localhost:5000**
Enter your Groq API key in the sidebar and start chatting!

---

## 🌐 Adding LawBot to Your Existing LegalQuestor Website

### Option A — Floating Chat Button (RECOMMENDED)
Add this to **every page** of your website (index.html, cyber.html, etc.)
Paste just before the closing `</body>` tag:

```html
<!-- LawBot Floating Button -->
<style>
  #lawbot-btn {
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    width: 60px; height: 60px;
    background: linear-gradient(135deg, #0d1b2a, #1a3a5c);
    border-radius: 50%; border: none; cursor: pointer;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    font-size: 26px; display: flex; align-items: center; justify-content: center;
    transition: transform 0.2s, box-shadow 0.2s;
    text-decoration: none;
  }
  #lawbot-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 28px rgba(0,0,0,0.4);
  }
  #lawbot-badge {
    position: absolute; top: -4px; right: -4px;
    width: 16px; height: 16px; background: #4caf82;
    border-radius: 50%; border: 2px solid white;
  }
</style>

<a id="lawbot-btn" href="http://localhost:5000" target="_blank" title="Ask LawBot">
  ⚖️
  <div id="lawbot-badge"></div>
</a>
<!-- End LawBot -->
```

### Option B — Embed as iframe in a chatbot page
Create a new file `chatbot.html` in your `public/` folder:

```html
<!DOCTYPE html>
<html>
<head>
  <title>LawBot - LegalQuestor</title>
  <style>
    body { margin: 0; padding: 0; height: 100vh; }
    iframe { width: 100%; height: 100vh; border: none; }
  </style>
</head>
<body>
  <iframe src="http://localhost:5000" title="LawBot"></iframe>
</body>
</html>
```

Then link to it from your navbar:
```html
<a href="chatbot.html">🤖 LawBot</a>
```

### Option C — Link directly from navbar
In your `index.html` navbar, add:
```html
<a href="http://localhost:5000" target="_blank" class="nav-link">⚖️ LawBot</a>
```

---

## 🚀 Deployment (To put online for everyone)

### Backend — Deploy on Render.com (FREE)
1. Push your `lawbot/` folder to GitHub
2. Go to https://render.com → New Web Service
3. Connect your repo
4. Set:
   - **Build command**: `pip install -r requirements.txt && python setup_index.py`
   - **Start command**: `python backend/app.py`
5. Get your live URL like: `https://lawbot-xyz.onrender.com`

### Update frontend URL
In `frontend/index.html`, change:
```js
const BACKEND_URL = 'http://localhost:5000';
```
to your Render URL:
```js
const BACKEND_URL = 'https://lawbot-xyz.onrender.com';
```

---

## 🧠 How RAG Works in LawBot

```
User asks: "What is punishment for theft?"
         ↓
TF-IDF Search → finds top 5 relevant chunks from IPC/BNS/CrPC
         ↓
Chunks sent as context to Groq LLM (LLaMA 3)
         ↓
LLM generates accurate answer grounded in actual law text
         ↓
Response shown to user with source citations (IPC / BNS / etc.)
```

---

## 📌 Tech Stack
| Layer | Technology |
|-------|-----------|
| AI Model | LLaMA 3 (8B) via Groq API |
| RAG Search | TF-IDF + Cosine Similarity (scikit-learn) |
| Backend | Python Flask |
| Frontend | HTML + CSS + Vanilla JS |
| PDF Processing | pypdf |
| Legal Corpus | IPC, BNS, CrPC, PWDVA (4 docs, ~2500 chunks) |

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|---------|
| `Cannot connect to backend` | Make sure `python backend/app.py` is running |
| `Invalid API Key` | Get key from console.groq.com, starts with `gsk_` |
| `No module named flask` | Run `pip install -r requirements.txt` |
| Empty answers | Check that setup_index.py ran successfully |

---

*Built for LegalQuestor Final Year Project*
