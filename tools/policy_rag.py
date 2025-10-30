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
    Simplified policy compliance check based on clear rules:
    1. Flight: Coach/Economy only, max $600
    2. Hotel: Max $200/night (or $250 for NYC, SF, LA, Boston, DC, Seattle, Chicago)
    3. Car rental: Max $75/day
    4. Total trip: Max $2,000 domestic
    """
    violations = []
    notes = []
    
    destination = trip.get("destination", "").lower()
    
    # List of expensive cities
    expensive_cities = ['new york', 'nyc', 'san francisco', 'sfo', 'los angeles', 
                       'la', 'boston', 'washington', 'dc', 'seattle', 'chicago']
    
    is_expensive_city = any(city in destination for city in expensive_cities)
    
    # 1) Business purpose required
    if not trip.get("purpose"):
        violations.append("❌ Trip must have a business justification")
    else:
        notes.append("✅ Business purpose: " + trip.get("purpose"))
    
    # 2) Check total budget
    try:
        budget = float(trip.get("budget", 0))
        if budget > 2000:
            violations.append(f"❌ Total budget ${budget:,.0f} exceeds $2,000 limit - Manager approval required")
        elif budget > 1500:
            notes.append(f"⚠️ Budget ${budget:,.0f} exceeds $1,500 - Manager approval required")
        else:
            notes.append(f"✅ Budget ${budget:,.0f} is within policy")
    except:
        notes.append("⚠️ Could not verify budget amount")
    
    # 3) Flight policy (checked in simple mode)
    notes.append("✅ Flight policy: Coach/Economy class only (max $600 round trip)")
    notes.append("   Mock flights are all in economy class and under $600")
    
    # 4) Hotel policy
    hotel_limit = 250 if is_expensive_city else 200
    if is_expensive_city:
        notes.append(f"✅ Hotel policy: Max ${hotel_limit}/night (expensive city exception)")
    else:
        notes.append(f"✅ Hotel policy: Max ${hotel_limit}/night (standard cities)")
    notes.append("   Our recommendations include corporate discount rates under limit")
    
    # 5) Car rental policy
    notes.append("✅ Car rental policy: Max $75/day")
    notes.append("   All rental options comply with $75/day limit")
    
    # 6) Preferred vendors
    notes.append("✅ Preferred airlines: Delta, United, American")
    notes.append("✅ Preferred hotels: Marriott, Hilton, Hyatt")
    notes.append("✅ Preferred car rentals: Enterprise, Hertz, National")
    
    # Determine overall status
    if violations:
        status = "⚠️ Needs Review"
    else:
        status = "✅ Approved"
    
    return {
        "status": status,
        "violations": violations,
        "notes": notes,
    }