<<<<<<< HEAD
# AI Freelancing Automation Agency

Production-ready multi-agent AI system that automates freelance job discovery, proposal generation, and pricing suggestions using **free, open-source job platforms**.

## 🎯 Features

- **Multi-Source Job Scraping**: Automatically fetches jobs from RemoteOK, We Work Remotely, and Adzuna (all free!)
- **AI-Powered Filtering**: Uses LLM to filter relevant jobs based on your criteria
- **Proposal Generation**: GPT-4 powered custom proposal writing
- **Smart Pricing**: AI-suggested competitive pricing with rationale
- **Vector Memory**: ChromaDB for storing job and proposal history
- **Manual Submission**: Safe copy-paste workflow (no automated submissions)
- **REST API**: FastAPI backend with JWT authentication
- **Dashboard**: Beautiful Streamlit frontend
- **LangGraph Orchestration**: Multi-agent workflow management

## 📁 Project Structure

```
ai-freelancing-agency/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # SQLAlchemy models
│   ├── db/
│   │   ├── session.py          # Database session
│   │   ├── init_db.py          # Database initialization
│   │   └── crud.py             # CRUD operations
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── agents/
│   │   ├── job_scout.py        # Job scraping orchestration
│   │   ├── filter_agent.py     # Job relevance filtering
│   │   ├── proposal_agent.py   # AI proposal generation
│   │   ├── pricing_agent.py    # Price suggestion
│   │   ├── memory_agent.py     # ChromaDB vector memory
│   │   └── submission_agent.py # Manual submission helper
│   └── graph/
│       └── workflow.py         # LangGraph orchestration
├── scraper/
│   ├── remoteok.py             # RemoteOK API scraper
│   ├── weworkremotely.py       # We Work Remotely RSS scraper
│   └── adzuna.py               # Adzuna API scraper
├── frontend/
│   └── dashboard.py            # Streamlit dashboard
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- OpenAI API key (for AI features)
- (Optional) Adzuna API key (free tier)

### Step 1: Clone/Download Project

```powershell
cd "C:\Users\Maneesh Kushram\.gemini\antigravity\scratch\ai-freelancing-agency"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your credentials:

```env
# Database (Install PostgreSQL first)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/freelancing_agency

# OpenAI API Key (Get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-openai-api-key-here

# JWT Secret (Generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here

# Optional: Adzuna API (Get from https://developer.adzuna.com/)
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key
```

### Step 5: Setup PostgreSQL Database

**Install PostgreSQL:**
1. Download from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for `postgres` user

**Create Database:**

```powershell
# Open PowerShell and run:
psql -U postgres
```

In PostgreSQL prompt:

```sql
CREATE DATABASE freelancing_agency;
\q
```

### Step 6: Initialize Database

```powershell
python -m backend.db.init_db
```

You should see: `✓ Database tables created successfully!`

## 🎮 Usage

### Running the Backend

```powershell
python -m uvicorn backend.main:app --reload
```

Backend will start at: http://localhost:8000

- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api

### Running the Frontend

Open a **new terminal** (keep backend running):

```powershell
cd "C:\Users\Maneesh Kushram\.gemini\antigravity\scratch\ai-freelancing-agency"
.\venv\Scripts\Activate.ps1
python -m streamlit run frontend/dashboard.py
```

Dashboard will open at: http://localhost:8501

### Using the Dashboard

1. **Run Workflow**: Click "Run Workflow" in sidebar
2. **View Jobs**: Check discovered jobs in "Jobs" page
3. **View Proposals**: See generated proposals in "Proposals" page
4. **Copy & Submit**: Manually copy proposals and submit to job platforms

## 🧪 Testing

### Test Individual Components

**Test Scrapers:**

```powershell
# Test RemoteOK
python -m scraper.remoteok

# Test We Work Remotely
python -m scraper.weworkremotely

# Test Adzuna
python -m scraper.adzuna
```

**Test Agents:**

```powershell
# Test Job Scout
python -m backend.agents.job_scout

# Test Filter Agent
python -m backend.agents.filter_agent

# Test Proposal Agent
python -m backend.agents.proposal_agent
```

**Test Workflow:**

```powershell
python -m backend.graph.workflow
```

### Test API Endpoints

```powershell
# Health check
curl http://localhost:8000/health

# Get jobs
curl http://localhost:8000/api/jobs

# Run workflow
curl -X POST http://localhost:8000/api/workflow/run
```

## 🔧 Common Issues & Fixes

### Issue 1: "ModuleNotFoundError"

**Solution:** Make sure virtual environment is activated:

```powershell
.\venv\Scripts\Activate.ps1
```

### Issue 2: "Could not connect to database"

**Solutions:**
1. Check PostgreSQL is running:
   ```powershell
   Get-Service postgresql*
   ```
2. Verify DATABASE_URL in `.env`
3. Create database if missing:
   ```sql
   CREATE DATABASE freelancing_agency;
   ```

### Issue 3: "OpenAI API Error"

**Solutions:**
1. Verify OPENAI_API_KEY in `.env`
2. Check API key is valid at https://platform.openai.com/api-keys
3. Ensure you have credits in your OpenAI account

### Issue 4: "Cannot connect to API" in Dashboard

**Solution:** Make sure backend is running:

```powershell
python -m uvicorn backend.main:app --reload
```

### Issue 5: "playwright install" error

**Solution:** Install Playwright browsers (only if using Playwright):

```powershell
playwright install
```

### Issue 6: ChromaDB errors

**Solution:** ChromaDB will auto-create the directory. If issues persist:

```powershell
Remove-Item -Recurse -Force .\chroma_db
```

Then restart the application.

## 📊 How It Works

### Workflow Pipeline

```
1. Job Scout Agent
   ↓ Scrapes jobs from RemoteOK, We Work Remotely, Adzuna
   
2. Filter Agent
   ↓ Uses LLM to filter relevant jobs
   
3. Proposal Agent
   ↓ Generates custom proposals with GPT-4
   
4. Pricing Agent
   ↓ Suggests competitive pricing
   
5. Memory Agent
   ↓ Stores in ChromaDB vector database
   
6. Submission Agent
   ↓ Prepares for manual copy-paste submission
```

### Free Job Sources

- **RemoteOK**: Public API, no authentication needed
- **We Work Remotely**: RSS feed, completely free
- **Adzuna**: Free tier API (optional, requires free registration)

## 🔐 Security Notes

- Never commit `.env` file to version control
- Change `SECRET_KEY` in production
- Use strong PostgreSQL password
- Keep OpenAI API key secure
- Review all proposals before submitting

## 💰 Cost Considerations

- **RemoteOK**: Free
- **We Work Remotely**: Free
- **Adzuna**: Free tier (limited requests)
- **OpenAI API**: Pay-per-use
  - GPT-3.5-turbo: ~$0.002 per request
  - GPT-4: ~$0.03 per request
  - Limit proposals to control costs

## 🎯 Next Steps

1. **Customize Filters**: Edit `backend/agents/filter_agent.py` to match your skills
2. **Improve Proposals**: Modify prompt in `backend/agents/proposal_agent.py`
3. **Add More Sources**: Create new scrapers in `scraper/` directory
4. **Deploy**: Use Docker, Heroku, or AWS for production deployment

## 📝 License

This project is for educational purposes. Respect terms of service of job platforms.

## 🤝 Support

For issues or questions:
1. Check the "Common Issues" section above
2. Review API documentation at http://localhost:8000/docs
3. Check individual agent test outputs

---

**Built with ❤️ using FastAPI, LangGraph, and LangChain**
=======
# Freelancer-AI
# Freelancer-AI
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
