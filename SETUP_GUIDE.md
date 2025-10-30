# AI Travel Booker - Setup Guide

## 🎯 Project Overview

This is a corporate travel planning application powered by AI agents. It demonstrates:
- **Local-first AI** using Ollama (privacy & security)
- **Multi-agent system** with CrewAI framework
- **Intelligent recommendations** based on travel history
- **Policy compliance** checking with RAG
- **Trip enrichment** (weather, restaurants, warnings)
- **Booking workflow** (mock for demo)

## 📋 Prerequisites

### Required
- Python 3.10 or higher
- pip (Python package manager)

### Optional (for CrewAI mode)
- [Ollama](https://ollama.com) - Local LLM runtime

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `gradio` - Web UI framework
- `crewai` - Agent framework
- `sentence-transformers` - For embeddings (RAG)
- `faiss-cpu` - Vector database
- `duckduckgo-search` - Web search
- `pandas`, `openpyxl` - Excel support
- `langchain-ollama` - Ollama integration

### 2. Run the Application

**Option A: Simple Mode (No LLM required)**
```bash
python app_gradio_enhanced.py
```

This mode:
- ✅ Works immediately, no setup needed
- ✅ Fast responses (< 2 seconds)
- ✅ Uses tools directly (search, analysis, policy check)
- ❌ No AI agent reasoning

**Option B: CrewAI Mode (Full AI agents)**

First, install and run Ollama:

```bash
# Install Ollama from: https://ollama.com

# Start Ollama server
ollama serve

# In another terminal, download a model
ollama pull llama3.2

# Or use alternative models:
# ollama pull mistral
# ollama pull phi3
# ollama pull gemma
```

Then run the app and check "Use CrewAI Agents" in the UI.

### 3. Open the Web Interface

Navigate to: http://localhost:7860

## 📁 Project Structure

```
travelplanner/
├── app_gradio_enhanced.py     # Main UI (enhanced version)
├── app_gradio.py              # Original simple UI
├── crew_setup_new.py          # New orchestrator with agent support
├── crew_setup.py              # Original simple orchestrator
├── requirements.txt           # Python dependencies
├── SETUP_GUIDE.md            # This file
│
├── agents/
│   ├── __init__.py
│   └── travel_agents.py       # CrewAI agent definitions
│
├── tools/
│   ├── __init__.py
│   ├── travel_tools.py        # Original mock tools
│   ├── web_search.py          # Enhanced flight/hotel search
│   ├── travel_history.py      # Preference analysis
│   ├── trip_research.py       # Destination intelligence
│   ├── booking.py             # Booking workflow
│   └── policy_rag.py          # Policy compliance with RAG
│
└── data/
    ├── sample_travel_history.xlsx  # Example travel history (CSV format)
    ├── travel_profile.json         # User profile & preferences
    ├── company_policy.md           # Corporate travel policy
    └── booking_history.json        # Saved bookings (generated)
```

## 🔧 Configuration

### Customize Travel History

Edit `data/sample_travel_history.xlsx` (CSV format):

```csv
Trip Code,Origin,Destination,Airline,Hotel,Flight Class,Rental Car,Trip Date,Total Cost
TRP001,Chicago,New York,Delta,Marriott Marquis,Economy,Enterprise,2024-03-15,1250
```

Columns:
- **Trip Code**: Unique identifier
- **Airline**: Preferred carrier (Delta, United, American, etc.)
- **Hotel**: Hotel name (include brand: Marriott, Hilton, etc.)
- **Flight Class**: Economy, Premium Economy, Business
- **Rental Car**: Company name or "None"

### Customize Travel Profile

Edit `data/travel_profile.json`:

```json
{
  "personal_info": {
    "full_name": "Your Name",
    "email": "your.email@company.com",
    "employee_id": "EMP12345"
  },
  "travel_preferences": {
    "seat_preference": "Aisle",
    "loyalty_programs": {
      "airlines": ["Delta SkyMiles: DL123456789"],
      "hotels": ["Marriott Bonvoy: MB555666777"]
    }
  }
}
```

### Customize Company Policy

Edit `data/company_policy.md` with your company's rules:
- Flight class restrictions
- Hotel rate limits
- Booking advance requirements
- Approval thresholds

## 🤖 CrewAI Agents Explained

When using CrewAI mode, these agents work together:

1. **Travel Planning Coordinator**
   - Orchestrates the entire workflow
   - Searches flights & hotels
   - Analyzes user preferences
   - Creates top 5 package recommendations

2. **Policy Compliance Officer**
   - Reviews all recommendations
   - Checks against company policy
   - Flags violations
   - Suggests compliant alternatives

3. **Destination Research Specialist**
   - Gathers destination intelligence
   - Weather forecast
   - Restaurant recommendations
   - Travel warnings
   - Things to do

4. **Booking Specialist** (future)
   - Executes final reservations
   - Applies loyalty programs
   - Sends confirmations

## 🔐 Security Features

### Current (Demo)
- Local data storage (no cloud)
- Mock payment processing
- Sensitive data marked with warnings

### Production Recommendations
1. **Encryption**: Use Fernet or AWS KMS for payment/passport data
2. **Authentication**: Add user login (OAuth, SSO)
3. **Audit logging**: Track all bookings and policy exceptions
4. **Network isolation**: Run Ollama in secure network
5. **Data retention**: Implement retention policies

## 🌐 Web Scraping (Production)

The current version uses mock data. To integrate real data:

### Flights
- **Google Flights**: Use Playwright/Selenium
- **Amadeus API**: Commercial flight API
- **Skyscanner API**: Flight aggregator
- **Airline APIs**: Direct integration (Delta, United, etc.)

### Hotels
- **Booking.com API**: Partner program required
- **Hotels.com API**: Expedia Group API
- **Hotel Chain APIs**: Marriott, Hilton, Hyatt

### Weather
- **OpenWeatherMap API**: Free tier available
- **WeatherAPI.com**: Free tier available

### Travel Warnings
- **US State Department**: Scrape travel.state.gov
- **CDC Travel Notices**: Scrape wwwnc.cdc.gov/travel

## 🐛 Troubleshooting

### "CrewAI mode failed"
**Solution**: Make sure Ollama is running
```bash
ollama serve
```

### "Model not found"
**Solution**: Download the model
```bash
ollama pull llama3.2
```

### "Connection refused localhost:11434"
**Solution**: Ollama is not running. Start it with `ollama serve`

### Slow responses in CrewAI mode
**Expected**: First request takes 30-60s (model loading)
**Subsequent**: Should be faster (5-15s)
**Tip**: Use Simple Mode for faster results

### Import errors
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Excel file not loading
**Solution**: The sample file is in CSV format despite .xlsx extension
```bash
# Save as proper CSV or install:
pip install openpyxl
```

## 📊 Testing the System

### Test 1: Simple Mode
1. Run: `python app_gradio_enhanced.py`
2. Leave "Use CrewAI Agents" **unchecked**
3. Enter: "Plan my NYC trip"
4. Click "Plan Trip"
5. Should get results in < 3 seconds

### Test 2: CrewAI Mode
1. Start Ollama: `ollama serve`
2. Check "Use CrewAI Agents"
3. Enter: "I need to visit our SF office"
4. Wait 30-60 seconds for first response
5. Review agent reasoning in console

### Test 3: Preference Learning
1. Edit `data/sample_travel_history.xlsx`
2. Add multiple trips with Delta
3. Run a new search
4. Verify Delta flights are marked with ⭐

## 🚀 Next Steps

### Phase 1: Core Enhancements
- [ ] Real web scraping with DuckDuckGo
- [ ] Better Excel parsing (actual .xlsx support)
- [ ] Enhanced policy RAG with better chunking
- [ ] Streaming responses in Gradio

### Phase 2: Advanced Features
- [ ] Multi-city trips
- [ ] Team travel coordination
- [ ] Budget approval workflow
- [ ] Expense report generation

### Phase 3: Production Ready
- [ ] User authentication
- [ ] Database backend (PostgreSQL)
- [ ] Real booking API integration
- [ ] Email notifications
- [ ] Mobile app (React Native)

## 📚 Resources

- **Ollama**: https://ollama.com
- **CrewAI Docs**: https://docs.crewai.com
- **Gradio Docs**: https://gradio.app/docs
- **LangChain**: https://python.langchain.com

## 💬 Support

For issues:
1. Check this guide first
2. Review console output for errors
3. Ensure all dependencies are installed
4. Try Simple Mode first to isolate LLM issues

## 📝 License

This is a demo/educational project. For production use:
- Review security implementation
- Obtain proper API licenses
- Comply with data protection regulations (GDPR, CCPA)
- Get travel supplier agreements

