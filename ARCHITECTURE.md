# System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                              │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Gradio Web UI                             │  │
│  │  • Chat interface                                            │  │
│  │  • Trip parameters form                                       │  │
│  │  • Mode selection (Simple/CrewAI)                           │  │
│  │  • Booking confirmation                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTP/WebSocket
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                             │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              crew_setup_new.py                               │   │
│  │                                                               │   │
│  │  def run_travel_crew(params, mode, use_crewai):             │   │
│  │      if use_crewai:                                          │   │
│  │          return run_travel_crew_ai(params)  # CrewAI        │   │
│  │      else:                                                    │   │
│  │          return run_simple_mode(params)     # Direct Tools  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────┬─────────────────────────────┬───────────────────────┘
                │                             │
        ┌───────┴────────┐           ┌────────┴────────┐
        │                │           │                 │
        ▼                ▼           ▼                 ▼
┌──────────────┐  ┌──────────────────────────────────────────┐
│   SIMPLE     │  │         CREWAI AGENT SYSTEM               │
│   MODE       │  │                                            │
│              │  │  ┌──────────────────────────────────┐    │
│  Direct      │  │  │   Travel Planning Coordinator    │    │
│  Tool        │  │  │   • Search flights & hotels      │    │
│  Calls       │  │  │   • Analyze preferences          │    │
│              │  │  │   • Create packages              │    │
│              │  │  └────────────┬─────────────────────┘    │
│              │  │               │                            │
│              │  │               ▼                            │
│              │  │  ┌──────────────────────────────────┐    │
│              │  │  │   Policy Compliance Officer      │    │
│              │  │  │   • Validate against rules       │    │
│              │  │  │   • RAG-based policy search     │    │
│              │  │  │   • Flag violations              │    │
│              │  │  └────────────┬─────────────────────┘    │
│              │  │               │                            │
│              │  │               ▼                            │
│              │  │  ┌──────────────────────────────────┐    │
│              │  │  │   Destination Research Specialist│    │
│              │  │  │   • Weather forecast             │    │
│              │  │  │   • Restaurant recommendations   │    │
│              │  │  │   • Travel warnings              │    │
│              │  │  └────────────┬─────────────────────┘    │
│              │  │               │                            │
│              │  │               ▼                            │
│              │  │  ┌──────────────────────────────────┐    │
│              │  │  │   Booking Specialist             │    │
│              │  │  │   • Execute reservations         │    │
│              │  │  │   • Generate confirmations       │    │
│              │  │  └──────────────────────────────────┘    │
│              │  │                                            │
│              │  │  Powered by: Ollama LLM (local)          │
└──────┬───────┘  └─────────────────┬──────────────────────────┘
       │                            │
       │     ┌──────────────────────┘
       │     │
       ▼     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           TOOLS LAYER                                │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Travel     │  │   Policy     │  │    Trip      │             │
│  │   History    │  │   RAG        │  │   Research   │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Web        │  │   Booking    │  │   Payment    │             │
│  │   Search     │  │   Workflow   │  │   Profile    │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                  │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Travel    │  │   Travel    │  │   Company   │                │
│  │   History   │  │   Profile   │  │   Policy    │                │
│  │   (.xlsx)   │  │   (.json)   │  │   (.md)     │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                       │
│  ┌─────────────┐  ┌─────────────────────────────┐                  │
│  │   Booking   │  │    Vector Store (FAISS)     │                  │
│  │   History   │  │    • Policy embeddings       │                  │
│  │   (.json)   │  │    • Semantic search         │                  │
│  └─────────────┘  └─────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow

### Simple Mode Flow

```
1. User Input
   ↓
2. Orchestrator (crew_setup_new.py)
   ↓
3. Direct Tool Execution
   ├─→ Load Travel History
   ├─→ Analyze Preferences
   ├─→ Search Flights
   ├─→ Search Hotels
   ├─→ Check Policy (RAG)
   └─→ Research Destination
   ↓
4. Rank & Format Results
   ↓
5. Return to UI
   
Time: < 3 seconds
```

### CrewAI Mode Flow

```
1. User Input
   ↓
2. Orchestrator (crew_setup_new.py)
   ↓
3. Initialize Agents + LLM (Ollama)
   ↓
4. Create Tasks
   ↓
5. Crew Execution (Sequential Process)
   │
   ├─→ Task 1: Travel Planner
   │   • Get traveler preferences (tool call)
   │   • Search flights (tool call)
   │   • Search hotels (tool call)
   │   • LLM: Analyze and create packages
   │   ↓
   ├─→ Task 2: Policy Officer
   │   • Review packages
   │   • Check policy compliance (tool call + RAG)
   │   • LLM: Flag violations, suggest alternatives
   │   ↓
   ├─→ Task 3: Research Specialist
   │   • Research destination (tool call)
   │   • LLM: Compile destination guide
   │   ↓
   └─→ Task 4: Travel Planner (Final)
       • LLM: Combine all info
       • LLM: Create final recommendation
   ↓
6. Return to UI

Time: 30-60 seconds (first), 5-15 seconds (subsequent)
```

## 🗄️ Data Flow

### Travel History Analysis

```
data/sample_travel_history.xlsx
            ↓
    [Load CSV/Excel]
            ↓
    [Parse Records]
            ↓
┌───────────────────────────┐
│ Trip Records              │
│ • Trip Code               │
│ • Origin/Destination      │
│ • Airline (preference)    │
│ • Hotel (preference)      │
│ • Flight Class            │
│ • Cost                    │
└───────────┬───────────────┘
            ↓
    [Analyze Patterns]
            ↓
┌───────────────────────────┐
│ Preferences Extracted     │
│ • Preferred Airlines      │
│ • Preferred Hotels        │
│ • Typical Flight Class    │
│ • Average Cost            │
└───────────┬───────────────┘
            ↓
    [Rank Search Results]
            ↓
┌───────────────────────────┐
│ Personalized Rankings     │
│ ⭐ Delta (5/7 trips)      │
│    United (2/7 trips)     │
│ ⭐ Marriott (6/7 stays)   │
│    Hilton (1/7 stays)     │
└───────────────────────────┘
```

### Policy Compliance (RAG)

```
data/company_policy.md
            ↓
    [Load Document]
            ↓
    [Split into Chunks]
            ↓
┌───────────────────────────┐
│ Policy Chunks (~300 words)│
│ • Flight policy           │
│ • Hotel policy            │
│ • Approval rules          │
│ • Expense limits          │
└───────────┬───────────────┘
            ↓
[Sentence Transformers]
[Create Embeddings]
            ↓
┌───────────────────────────┐
│ Vector Store (FAISS)      │
│ • 384-dim vectors         │
│ • Fast similarity search  │
└───────────┬───────────────┘
            │
            ├──→ Query: "hotel rate NYC"
            │         ↓
            │    [Semantic Search]
            │         ↓
            └──→ Top 3 Relevant Chunks:
                 1. "Tier 1 cities: $250/night max"
                 2. "Marriott preferred"
                 3. "Manager approval >$2500"
```

## 🧩 Component Interaction

### Agent → Tool → Data

```
┌──────────────────┐
│  Agent           │
│  "Search for     │ ──┐
│   flights to NYC"│   │
└──────────────────┘   │
                       │ (tool call)
                       ▼
            ┌──────────────────────┐
            │  Tool Function       │
            │  search_flights()    │
            │  • origin            │ ──┐
            │  • destination       │   │
            │  • dates             │   │
            └──────────────────────┘   │
                                       │ (data access)
                                       ▼
                            ┌─────────────────────┐
                            │  External Data      │
                            │  • Mock API         │
                            │  • Web Scraping     │
                            │  • Real API (future)│
                            └──────────┬──────────┘
                                       │
                                       │ (results)
                                       ▼
            ┌──────────────────────┐
            │  Formatted Results   │
            │  5 flight options    │
            │  with pricing        │
            └──────────┬───────────┘
                       │
                       │ (return)
                       ▼
┌──────────────────┐
│  Agent           │
│  "Here are 5     │
│   flight options"│
└──────────────────┘
```

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────┐
│            Security Layers                   │
│                                              │
│  Layer 1: Local-First                       │
│  • All processing local                     │
│  • No cloud API calls                       │
│  • Ollama runs localhost                    │
│                                              │
│  Layer 2: Data Protection                   │
│  • Travel history (local files)             │
│  • Payment info (encrypted/mock)            │
│  • No PII sent to LLM                       │
│                                              │
│  Layer 3: Access Control (Future)           │
│  • User authentication                      │
│  • Role-based access (RBAC)                 │
│  • Session management                       │
│                                              │
│  Layer 4: Audit & Monitoring (Future)       │
│  • All actions logged                       │
│  • Policy violations tracked                │
│  • Booking confirmations saved              │
│                                              │
│  Layer 5: Encryption (Future)               │
│  • Data at rest (Fernet/KMS)               │
│  • Data in transit (TLS)                    │
│  • Key rotation                             │
└─────────────────────────────────────────────┘
```

## 📊 Technology Stack

### Frontend
```
┌─────────────────┐
│    Gradio       │  ← Web UI framework
│                 │    • Python-based
│    • Blocks     │    • Reactive
│    • Chatbot    │    • WebSocket support
│    • Forms      │
└─────────────────┘
```

### Backend
```
┌─────────────────┐
│    Python       │  ← Core language
│                 │
│    • CrewAI     │  ← Agent framework
│    • LangChain  │  ← LLM orchestration
│    • Pandas     │  ← Data processing
└─────────────────┘
```

### AI/ML
```
┌─────────────────────────┐
│    Ollama               │  ← Local LLM runtime
│    • llama3.2           │
│    • mistral            │
│    • phi3               │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│  Sentence Transformers  │  ← Embeddings
│  • all-MiniLM-L6-v2     │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│       FAISS             │  ← Vector DB
│  • IndexFlatIP          │
│  • Fast similarity      │
└─────────────────────────┘
```

### Data Storage
```
┌─────────────────┐
│   File-Based    │  ← Current (demo)
│                 │
│   • Excel/CSV   │    Travel history
│   • JSON        │    Profiles, bookings
│   • Markdown    │    Policy docs
└─────────────────┘

┌─────────────────┐
│   Database      │  ← Future (production)
│                 │
│   • PostgreSQL  │    Relational data
│   • Redis       │    Caching
│   • S3/Blob     │    Document storage
└─────────────────┘
```

## 🔄 Deployment Options

### Local Development (Current)
```
┌─────────────────────────────────┐
│      Developer Machine          │
│                                  │
│  ┌────────────┐  ┌────────────┐│
│  │   Ollama   │  │   Python   ││
│  │   :11434   │  │   :7860    ││
│  └────────────┘  └────────────┘│
│                                  │
│  Access: http://localhost:7860  │
└─────────────────────────────────┘
```

### Corporate Deployment (Future)
```
┌─────────────────────────────────────────┐
│         Corporate Network                │
│                                          │
│  ┌────────────────┐                     │
│  │  Load Balancer │                     │
│  └────────┬───────┘                     │
│           │                              │
│    ┌──────┴──────┐                      │
│    │             │                      │
│    ▼             ▼                      │
│  ┌────┐       ┌────┐                   │
│  │App1│       │App2│  ← Multiple       │
│  └──┬─┘       └──┬─┘     instances     │
│     │            │                      │
│     └────┬───────┘                      │
│          │                              │
│          ▼                              │
│  ┌────────────────┐                    │
│  │   PostgreSQL   │  ← Shared DB       │
│  └────────────────┘                    │
│                                          │
│  ┌────────────────┐                    │
│  │     Redis      │  ← Cache           │
│  └────────────────┘                    │
│                                          │
│  ┌────────────────┐                    │
│  │  Ollama Cluster│  ← LLM pool        │
│  └────────────────┘                    │
└─────────────────────────────────────────┘
```

## 🎯 Scalability Considerations

### Horizontal Scaling
```
Request → Load Balancer
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
  [App1]  [App2]  [App3]
    │        │        │
    └────────┼────────┘
             │
             ▼
      Shared Database
```

### Vertical Scaling
```
Simple Mode:
• CPU: 2 cores
• RAM: 2 GB
• Handles: 50+ concurrent users

CrewAI Mode:
• CPU: 8 cores (LLM inference)
• RAM: 8 GB (model in memory)
• GPU: Optional (2x faster)
• Handles: 10-20 concurrent users
```

## 📈 Performance Optimization

### Caching Strategy
```
Request: "Flights Chicago → NYC"
         ↓
    [Check Cache]
         ↓
    Cache Hit? ─→ Yes → Return cached results (< 100ms)
         │
         No
         ↓
    [Search APIs]
         ↓
    [Cache Results]  (TTL: 15 minutes)
         ↓
    [Return to User]  (2-3 seconds)
```

### Database Indexing
```sql
-- For fast lookups
CREATE INDEX idx_user_history 
  ON travel_history(user_id, trip_date);

CREATE INDEX idx_policy_search 
  ON policy_chunks USING GIN(content_vector);
```

## 🔍 Monitoring & Observability

### Metrics to Track
```
Application Metrics:
• Request rate (req/sec)
• Response time (p50, p95, p99)
• Error rate (%)
• Active users

Agent Metrics:
• Task completion time
• Tool call latency
• LLM token usage
• Agent success rate

Business Metrics:
• Bookings completed
• Policy violations
• Average trip cost
• User satisfaction
```

## 🏁 Summary

**Architecture Type**: Modular, Event-Driven, Agent-Based

**Key Characteristics**:
- 🎯 Separation of concerns (UI, Orchestration, Tools, Data)
- 🔌 Pluggable components (easy to swap tools/agents)
- 🔒 Security-first design (local processing)
- 📈 Scalable (horizontal scaling ready)
- 🧪 Testable (tools can be mocked)
- 📚 Well-documented (inline + external docs)

**Production Readiness**: 70%
- ✅ Core architecture solid
- ✅ Agent framework working
- ✅ Tool system extensible
- ⚠️ Needs real APIs
- ⚠️ Needs authentication
- ⚠️ Needs production database

---

**Next Steps**: See [SETUP_GUIDE.md](SETUP_GUIDE.md) for deployment instructions.

