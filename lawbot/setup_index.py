"""
setup_index.py — Run this ONCE to build the legal document index.
Place your PDF files in the legal_docs/ folder first.

Usage:
    python setup_index.py
"""

import os, json, pickle
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = os.path.join(os.path.dirname(__file__), 'legal_docs')
BACKEND  = os.path.join(os.path.dirname(__file__), 'backend')

# ── Map filenames to short labels ────────────────────────────────────────────
PDF_LABELS = {
    'IPC.pdf':   'IPC',
    'BNS.pdf':   'BNS',
    'CrPC.pdf':  'CrPC',
    'PWDVA.pdf': 'PWDVA',
}

def extract_and_chunk(pdf_path: str, label: str, chunk_words=150, overlap=30):
    reader = PdfReader(pdf_path)
    print(f"  {label}: {len(reader.pages)} pages")
    full_text = "\n".join(
        page.extract_text() or "" for page in reader.pages
    )
    words  = full_text.split()
    chunks = []
    for i in range(0, len(words), chunk_words - overlap):
        text = " ".join(words[i : i + chunk_words])
        if len(text) > 80:
            chunks.append({"source": label, "text": text})
    return chunks

def main():
    os.makedirs(BACKEND, exist_ok=True)
    all_chunks = []

    print("📚 Reading legal PDFs...")
    for filename, label in PDF_LABELS.items():
        path = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(path):
            print(f"  ⚠️  {filename} not found — skipping")
            continue
        chunks = extract_and_chunk(path, label)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("❌ No PDFs found. Put IPC.pdf, BNS.pdf, CrPC.pdf, PWDVA.pdf in legal_docs/")
        return

    # Assign IDs
    for i, c in enumerate(all_chunks):
        c["id"] = i

    print(f"\n✅ Total chunks: {len(all_chunks)}")

    # ── Build TF-IDF index ───────────────────────────────────────────────────
    print("🔍 Building TF-IDF index...")
    texts = [c["text"] for c in all_chunks]
    vectorizer = TfidfVectorizer(
        max_features=12000,
        ngram_range=(1, 2),
        stop_words="english"
    )
    matrix = vectorizer.fit_transform(texts)
    print(f"   Matrix shape: {matrix.shape}")

    # ── Save everything ──────────────────────────────────────────────────────
    with open(os.path.join(BACKEND, "chunks.json"), "w") as f:
        json.dump(all_chunks, f)
    with open(os.path.join(BACKEND, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(BACKEND, "matrix.pkl"), "wb") as f:
        pickle.dump(matrix, f)

    print("💾 Saved: chunks.json, vectorizer.pkl, matrix.pkl")
    print("\n🚀 Setup complete! Now run:  python backend/app.py")

if __name__ == "__main__":
    main()
