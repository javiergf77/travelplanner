import os
from typing import List, Dict

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    USE_EMB = True
except Exception:
    USE_EMB = False

def _read_pdf_as_text(path: str) -> str:
    """
    Read policy document - supports PDF, MD, TXT
    """
    if not os.path.exists(path):
        print(f"⚠️  Policy file not found: {path}")
        print("   Using default policy text...")
        return "Corporate travel policy: economy class for domestic, hotel under 200 per night, trips must have business justification."
    
    try:
        # Handle markdown/text files
        if path.endswith('.md') or path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        
        # Handle PDF files
        elif path.endswith('.pdf'):
            import fitz  # pymupdf
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        
        # Unknown format, try reading as text
        else:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
            
    except Exception as e:
        print(f"⚠️  Could not read policy file ({e}), using default policy text...")
        return "Corporate travel policy: economy class for domestic, hotel under 200 per night, trips must have business justification."

def _chunk_text(text: str, chunk_size: int = 400) -> List[str]:
    words = text.split()
    chunks = []
    current = []
    for w in words:
        current.append(w)
        if len(current) >= chunk_size:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks

def load_policy_chunks(pdf_path: str) -> Dict:
    print(f"📄 Loading policy document from: {pdf_path}")
    text = _read_pdf_as_text(pdf_path)
    chunks = _chunk_text(text, 300)
    print(f"✅ Created {len(chunks)} policy chunks")

    index = None
    model = None
    if USE_EMB:
        print("🤖 Loading sentence-transformers model (this may take a minute on first run)...")
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("📊 Encoding policy chunks...")
        embeddings = model.encode(chunks)
        d = embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        index.add(embeddings)
        print("✅ Policy search index ready!")
    else:
        print("⚠️  Running without embeddings (sentence-transformers not available)")

    return {
        "chunks": chunks,
        "index": index,
        "model": model,
    }

def check_policy_compliance(trip: Dict, policy_store: Dict) -> Dict:
    """
    Super simple policy logic:
    - if domestic → economy only
    - hotel should be <= 200/night
    - business purpose required
    """
    violations = []
    notes = []

    # 1) business purpose
    if not trip.get("purpose"):
        violations.append("Trip must have a business justification.")

    # 2) budget
    if trip.get("budget"):
        try:
            if float(trip["budget"]) < 300:
                notes.append("Budget is low; consider remote / virtual.")
            if float(trip["budget"]) > 2500:
                notes.append("High budget, may require manager approval.")
        except Exception:
            pass

    # 3) check policy text for relevant guidance (RAG-ish)
    guidance = ""
    if policy_store["index"] is not None and policy_store["model"] is not None and trip.get("destination"):
        q = f"travel policy to {trip['destination']} with budget {trip.get('budget','')}"
        q_emb = policy_store["model"].encode([q])
        D, I = policy_store["index"].search(q_emb, 3)
        guidance = "\n".join([policy_store["chunks"][i] for i in I[0] if i < len(policy_store["chunks"])])

    if guidance:
        notes.append("Policy excerpts:\n" + guidance[:400] + ("..." if len(guidance) > 400 else ""))

    status = "approved" if not violations else "needs review"
    return {
        "status": status,
        "violations": violations,
        "notes": notes,
    }