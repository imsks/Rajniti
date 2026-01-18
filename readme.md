# Rajniti (Flask + Postgres + Next.js)

Short, batteries-included Indian election API. Ships with JSON datasets, auto-migrations, and a tiny auto-seed so new contributors can query data immediately.

## Quick Start (Docker, local Postgres)
```bash
# create .env with the values below
docker compose --profile local-db up -d --build
# API → http://localhost:8000
```

## Quick Start (hosted DB, e.g., Supabase)
```bash
export DATABASE_URL=postgresql://<user>:<pass>@<host>:<port>/<db>
python run.py  # uses your DATABASE_URL, runs migrations, seeds if empty
```

## Auto migrations + auto seed
- Migrations run on startup.
- If the DB has zero candidates, a small slice of `app/data/lok_sabha/lok-sabha-2024` is loaded automatically.
- Controls:
  - `AUTO_POPULATE_DB` (default: true)
  - `AUTO_POPULATE_ELECTION_DIR` (default: `app/data/lok_sabha/lok-sabha-2024`)
  - `AUTO_POPULATE_LIMIT` (default: 500 candidates)

## Minimal .env (Docker/local)
```
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
SECRET_KEY=dev-secret-key
POSTGRES_USER=rajniti
POSTGRES_PORT=5432
DATABASE_URL=postgresql://rajniti:rajniti_dev_password@postgres:5432/rajniti
AUTO_POPULATE_DB=true
AUTO_POPULATE_LIMIT=500
```
Optional: `PERPLEXITY_API_KEY`, `OPENAI_API_KEY`, `CHROMA_DB_PATH`.

## Useful commands
- `docker compose --profile local-db up -d --build` — run API + local Postgres.
- `docker compose logs -f` — view logs.
- `python scripts/db.py migrate` — import full JSON data.
- `python scripts/db.py sync` — auto-generate & apply migrations.
- `python scripts/db.py reset` — drop and recreate tables (destructive).

## Project map
- `app/` Flask API, routes/controllers/services.
- `app/data/` JSON election data (used for seeding).
- `app/database/` models, migrations runner, auto-seed.
- `frontend/` Next.js landing page.
- `scripts/` DB + data utilities.

## Health + docs
- Health: `http://localhost:8000/api/v1/health`
- API docs (JSON): `http://localhost:8000/api/v1/doc`

## Contributing
- Keep changes small, add tests where it makes sense.
- Run `docker compose --profile local-db up -d --build` before opening PRs to ensure migrations + seed still work.
# 🗳️ Rajniti - Simple Election Data API

> **A clean, lightweight Flask API for Indian election data with a beautiful landing page**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![API Version](https://img.shields.io/badge/API-v1.0-orange.svg)](#api-documentation)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Data Coverage](https://img.shields.io/badge/Data-50K%2B_Records-purple.svg)](#data-coverage)

A simple, clean REST API serving Indian Election Commission data from JSON files. Building with minimal Flask setup for easy deployment and scraping capabilities. Includes a beautiful, India-themed landing page built with Next.js.

## 🚢 Quick Deployment

| Platform          | Type       | Command                | Status   |
| ----------------- | ---------- | ---------------------- | -------- |
| **Vercel**        | Frontend   | `vercel --prod`        | ✅ Ready |
| **GCP Cloud Run** | Backend    | `gcloud builds submit` | ✅ Ready |
| **Docker**        | Full Stack | `docker-compose up -d` | ✅ Ready |

👉 **Jump to**: [Vercel Deployment Guide](#deploy-to-vercel-) • [Backend Deployment](#deployment) • [Docker Setup](#option-1-docker-recommended)

---

## 🌟 **Key Features**

<div align="center">

| Feature                     | Description                                               |
| --------------------------- | --------------------------------------------------------- |
| 🚀 **Simple Flask API**     | Clean RESTful endpoints serving JSON data                 |
| 💾 **Database Support**     | PostgreSQL/Supabase support with easy migration           |
| 🤖 **AI-Powered Agent**     | Automated candidate data population using Perplexity AI   |
| 🔍 **Vector Search**        | ChromaDB-powered semantic search for candidates           |
| 🌐 **Landing Page**         | Beautiful Next.js landing page with India-themed design   |
| 📊 **Election Data**        | 50,000+ records across Lok Sabha & Assembly elections     |
| 🕸️ **Intelligent Scraping** | Advanced scraping system with retry logic & rate limiting |
| 📸 **Image Downloads**      | Candidate photos and party symbols extraction             |
| ⚡ **Lightweight**          | Minimal dependencies, fast startup                        |
| 🐳 **Docker Ready**         | Single container deployment                               |

</div>

---

## 📊 **Data Coverage**

<div align="center">

| Election                | Candidates  | Constituencies | Parties  | Status               |
| ----------------------- | ----------- | -------------- | -------- | -------------------- |
| **Lok Sabha 2024**      | 3,802+      | 543            | 211+     | ✅ Complete          |
| **Delhi Assembly 2025** | 6,922+      | 70             | 11+      | ✅ Complete          |
| **Maharashtra 2024**    | 39,817+     | 288            | 76+      | ✅ Complete          |
| **Total Coverage**      | **50,541+** | **901**        | **298+** | **🎯 Comprehensive** |

</div>

---

## 🚀 **Quick Start**

### **Option 1: Quick Start with Make (Recommended)**

```bash
# Clone the repository
git clone https://github.com/your-username/rajniti.git
cd rajniti

# One command to install, build, and start (uses pip-compile)
make

# API available at http://localhost:8000
# Health check: http://localhost:8000/api/v1/health
```

**What `make` does:**
- Creates virtual environment
- Installs pip-tools
- Compiles `requirements.txt` from `requirements.in` using `pip-compile`
- Installs all dependencies
- Builds Docker image
- Starts the application

### **Option 2: Docker Only**

```bash
# Clone the repository
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Start with Docker Compose
docker-compose up -d

# API available at http://localhost:8000
# Health check: http://localhost:8000/api/v1/health
```

### **Option 3: Manual Setup**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install pip-tools and compile dependencies
pip install --upgrade pip pip-tools
pip-compile requirements.in

# Install compiled dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run development server
python run.py
```

---

## 💾 **Database Support**

Rajniti now supports PostgreSQL database storage in addition to JSON files! Perfect for production deployments and works seamlessly with both local PostgreSQL and Supabase.

### **🎯 Features**

-   **Dual Storage**: Use JSON files or PostgreSQL database
-   **Supabase Ready**: Works out-of-the-box with Supabase
-   **Local PostgreSQL**: Full support for local development
-   **CRUD Operations**: Complete Create, Read, Update, Delete operations
-   **Easy Migration**: Script to migrate existing JSON data to database
-   **Automatic Migrations**: Idempotent migrations run automatically on server start

### **Quick Database Setup**

#### **Option 1: Local PostgreSQL**

```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew)
brew install postgresql

# Create database
createdb rajniti

# Set environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rajniti"

# Initialize database (create tables)
python scripts/db.py init

# Migrate JSON data to database
python scripts/db.py migrate
```

#### **Option 2: Supabase (Recommended for Production)**

```bash
# 1. Create a Supabase project at https://supabase.com
# 2. Get your database connection string from Project Settings → Database (URI format)
# 3. Set environment variable
export DATABASE_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"

# Initialize database (create tables)
python scripts/db.py init

# Migrate JSON data to database
python scripts/db.py migrate
```

### **Database Management Commands**

```bash
# Sync database with models (auto-generate & run migrations)
python scripts/db.py sync

# Initialize database (create tables)
python scripts/db.py init

# Migrate JSON data to database
python scripts/db.py migrate

# Preview migration without changes
python scripts/db.py migrate --dry-run

# Reset database (⚠️ deletes all data)
python scripts/db.py reset
```

**Note**: Migrations run automatically on server startup. Just update your models and start the server!

### **Database Models**

Three main models with full CRUD operations:

-   **Party**: Political parties (id, name, short_name, symbol)
-   **Constituency**: Electoral districts (id, name, state_id)
-   **Candidate**: Election candidates (id, name, party_id, constituency_id, state_id, status, type, image_url)

### **Using Database in Code**

```python
from app.database import get_db_session
from app.database.models import Party, Constituency, Candidate

# Create a party
with get_db_session() as session:
    party = Party.create(session, "123", "Example Party", "EP", "Lotus")

# Get all parties
with get_db_session() as session:
    parties = Party.get_all(session)

# Search candidates
with get_db_session() as session:
    candidates = Candidate.search_by_name(session, "Modi")
```

### **Configuration**

Set the `DATABASE_URL` environment variable to your PostgreSQL connection string:

```bash
# Local PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"

# Supabase
export DATABASE_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
```

📚 **Full documentation**: See [app/database/README.md](app/database/README.md) for detailed usage, migrations, and troubleshooting.

---

## 🌐 **Landing Page**

The Rajniti landing page is a beautiful, India-themed website built with Next.js 16, TypeScript, and Tailwind CSS.

### **Features**

-   🎨 **India-Themed Design**: Orange, white, and green color scheme
-   ⚡ **Server-Side Rendering**: Building with Next.js App Router for optimal performance
-   📱 **Fully Responsive**: Works seamlessly on all devices
-   🚀 **Easy Deployment**: Compatible with Vercel (recommended), GCP, and AWS

### **Quick Start (Frontend)**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Visit http://localhost:3000
```

### **Deploy to Vercel** 🚀

Deploy the Rajniti frontend to Vercel in just a few minutes! Vercel is the recommended platform for Next.js applications with excellent performance and developer experience.

#### **Step 1: Push to Git Repository**

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/your-username/rajniti.git
git push -u origin main
```

#### **Step 2: Deploy via Vercel Dashboard**

1. **Sign up** at [vercel.com](https://vercel.com/signup)
2. Click **"Add New Project"**
3. Import your **rajniti repository** from GitHub/GitLab/Bitbucket
4. Configure project settings:
    - **Framework Preset**: Next.js (auto-detected)
    - **Root Directory**: `frontend` ⚠️ **CRITICAL**: Set this to `frontend` for monorepo deployments
    - **Build Command**: `npm run build` (auto-detected)
    - **Output Directory**: Leave empty (Vercel handles this automatically for Next.js)
5. Click **"Deploy"**

**⚠️ Important**: If you get a 404 error after deployment, check that the **Root Directory** is set to `frontend` in your Vercel project settings. This is the most common cause of 404 errors in monorepo setups.

Vercel will automatically detect Next.js and configure everything for you!

#### **Step 3: Add Environment Variables (Optional)**

If you have a backend API, add this environment variable in Vercel:

1. Go to **Project Settings** → **Environment Variables**
2. Add variable:
    - **Key**: `NEXT_PUBLIC_API_URL`
    - **Value**: `https://your-backend-api.com`
    - **Environments**: Production, Preview, Development
3. Redeploy to apply changes

#### **Deploy via Vercel CLI**

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd frontend

# Deploy to production
vercel --prod
```

#### **Continuous Deployment**

Once connected to GitHub, Vercel automatically deploys when you push to `main`:

```bash
git add .
git commit -m "Update frontend"
git push origin main
# ✅ Vercel automatically rebuilds and deploys!
```

#### **Custom Domain (Optional)**

1. Go to **Project Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain name
4. Follow DNS configuration instructions

#### **Vercel Features**

-   ⚡ **Automatic HTTPS**: SSL certificates included
-   🌍 **Global CDN**: Fast content delivery worldwide
-   🔄 **Preview Deployments**: Automatic preview URLs for every PR
-   📊 **Analytics**: Built-in performance monitoring
-   🔒 **Security**: DDoS protection and security headers

---

### **Alternative Deployment Options**

````
**GCP Cloud Run:**

```bash
gcloud run deploy rajniti-frontend --source ./frontend
````

**Docker (Self-hosted):**

```bash
cd frontend
docker build -t rajniti-frontend .
docker run -p 3000:3000 rajniti-frontend
```

---

## 🕸️ **Data Scraping**

### **🎯 Overview**

Rajniti includes powerful scraping capabilities to collect fresh election data from the Election Commission of India (ECI) website. The scraping system is modular and supports both Lok Sabha and Assembly elections.

### **🚀 Quick Start Scraping**

#### **✨ NEW: Interactive Scraper (Recommended)**

The easiest way to scrape election data - just provide the URL!

```bash
# Activate virtual environment
source venv/bin/activate

# Run interactive scraper (auto-detects everything!)
python scripts/scrape_interactive.py

# You'll be prompted for:
# 1. Election Results URL (e.g., https://results.eci.gov.in/ResultAcGenFeb2025)
# 2. Election Type (LOK_SABHA or VIDHAN_SABHA)
# Everything else is auto-discovered!
```

#### **Legacy Scraping Methods**

```bash
# Direct URL scraping (no hardcoded values!)
python scripts/scrape_lok_sabha.py --url https://results.eci.gov.in/PcResultGenJune2024/index.htm
python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenFeb2025

# Legacy: State/Year based (constructs URLs automatically)
python scripts/scrape_lok_sabha.py --year 2024
python scripts/scrape_vidhan_sabha.py --state DL --year 2025

# Using Make commands
make setup  # Setup environment first
make scrape-help # Show scraping help
```

### **📋 Available Scrapers**

<div align="center">

| Scraper                  | Description                     | Command                            | Data Output                  |
| ------------------------ | ------------------------------- | ---------------------------------- | ---------------------------- |
| **✨ Interactive (NEW)** | URL-based, auto-discovery       | `scrape_interactive.py`            | Complete election data       |
| **🏛️ Lok Sabha**         | Parliamentary elections         | `scrape_lok_sabha.py --url URL`    | Candidates, Parties, Results |
| **🏛️ Vidhan Sabha**      | State assembly elections        | `scrape_vidhan_sabha.py --url URL` | Assembly candidates, Results |
| **🎯 Complete**          | All elections combined (legacy) | `scrape_all.py --year 2024`        | Comprehensive dataset        |

</div>

### **⚙️ Scraping Commands**

#### **✨ Interactive Scraper (Recommended)**

```bash
# Interactive mode - easiest way!
python scripts/scrape_interactive.py

# The script will guide you through:
# 1. Enter the ECI results URL
# 2. Confirm or select election type (auto-detected)
# 3. Review configuration
# 4. Start scraping with full auto-discovery!

# Example URLs you can use:
# - https://results.eci.gov.in/PcResultGenJune2024/index.htm         (Lok Sabha 2024)
# - https://results.eci.gov.in/ResultAcGenFeb2025     (Delhi 2025)
# - https://results.eci.gov.in/ResultAcGenOct2024     (Maharashtra 2024)
```

#### **Direct URL Scraping**

```bash
# Lok Sabha Elections (URL-based)
python scripts/scrape_lok_sabha.py --url https://results.eci.gov.in/PcResultGenJune2024/index.htm

# Vidhan Sabha Elections (URL-based)
python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenFeb2025

# Custom output directory
python scripts/scrape_lok_sabha.py --url URL --output-dir data/custom
python scripts/scrape_vidhan_sabha.py --url URL --output-dir data/custom
```

### **🏗️ Scraper Architecture (Simplified)**

```
app/scrapers/
├── base.py                    # 🔧 Utility functions (no classes)
│   ├── get_with_retry()       # HTTP requests with retry logic
│   ├── save_json()            # Save data to JSON files
│   ├── clean_votes()          # Clean vote count strings
│   └── clean_margin()         # Clean margin strings
├── lok_sabha.py              # 🏛️ Single Lok Sabha scraper
│   └── LokSabhaScraper       # One class that does everything
│       ├── scrape()          # Main orchestrator
│       ├── _scrape_parties() # Party data extraction
│       ├── _scrape_constituencies()  # Constituency discovery
│       ├── _scrape_candidates()      # Candidate data extraction
│       └── _extract_metadata()       # Election metadata
└── vidhan_sabha.py           # 🏛️ Single Vidhan Sabha scraper
    └── VidhanSabhaScraper    # One class that does everything
        ├── scrape()          # Main orchestrator
        ├── _detect_state_info()      # Auto-detect state & year
        ├── _scrape_parties()         # Party data extraction
        ├── _scrape_constituencies()  # Constituency discovery
        ├── _scrape_candidates()      # Candidate data extraction
        └── _save_all_data()          # Save all 4 JSON files

scripts/
└── scripts/scrape_interactive.py     # ✨ Interactive URL-based scraper
```

**Key Principles:**

-   ✅ No hardcoded state names, constituencies, or candidates
-   ✅ Everything scraped and auto-detected from ECI website
-   ✅ Auto-generates folder names from scraped data
-   ✅ Each scraper is self-contained - one URL input → 4 JSON outputs
-   ✅ Simple, linear flow: URL → Scrape → Save

### **📊 Data Sources & URLs**

The scrapers automatically fetch data from:

-   **Lok Sabha 2024**: `https://results.eci.gov.in/PcResultGenJune2024/index.htm/`
-   **Assembly Elections**: State-specific ECI result pages
-   **Party Results**: Party-wise winner lists
-   **Candidate Data**: Complete candidate profiles with photos
-   **Constituency Info**: Constituency-wise detailed results

### **⚡ Scraping Features**

-   **✨ Auto-Discovery**: Automatically finds constituencies and parties (NEW!)
-   **🌐 URL-Based**: No hardcoded values - works with any ECI URL (NEW!)
-   **🤖 Interactive Mode**: Guided scraping with smart defaults (NEW!)
-   **🔄 Retry Logic**: Automatic retry with exponential backoff
-   **🛡️ Rate Limiting**: Respectful scraping with delays
-   **📸 Image Downloads**: Candidate photos and party symbols
-   **🧹 Data Cleaning**: Automatic data normalization
-   **📁 JSON Output**: Clean, structured data files
-   **🔍 Error Handling**: Comprehensive error reporting
-   **📈 Progress Tracking**: Real-time scraping progress
-   **🎯 Flexible Scraping**: URL-based or legacy state/year modes

### **🛠️ Advanced Usage**

#### **Custom Scraping Configuration**

```python
from app.scrapers import LokSabhaScraper, VidhanSabhaScraper

# Simple URL-based scraping - everything auto-detected!
lok_sabha_scraper = LokSabhaScraper(
    url="https://results.eci.gov.in/PcResultGenJune2024/index.htm"
)

vidhan_sabha_scraper = VidhanSabhaScraper(
    url="https://results.eci.gov.in/ResultAcGenFeb2025"
)

# Run scraping - automatically:
# 1. Detects state/year from URL and page
# 2. Scrapes parties, constituencies, candidates
# 3. Generates folder name (e.g., "DL_2025_ASSEMBLY")
# 4. Saves 4 JSON files in proper structure
lok_sabha_scraper.scrape()
vidhan_sabha_scraper.scrape()

# Data is saved to:
# - app/data/lok_sabha/lok-sabha-{year}/
# - app/data/vidhan_sabha/{STATE}_{YEAR}_ASSEMBLY/
# - app/data/elections/ (metadata files)
```

#### **Environment Variables**

```bash
# Configure scraping behavior
export ECI_BASE_URL="https://results.eci.gov.in"
export SCRAPER_RETRY_ATTEMPTS=3
export SCRAPER_RETRY_DELAY=2
export SCRAPER_TIMEOUT=30
```

### **🎭 Supported Elections**

<div align="center">

| Election Type      | Years Available  | States Supported | Status        |
| ------------------ | ---------------- | ---------------- | ------------- |
| **Lok Sabha**      | 2024, 2019, 2014 | All India        | ✅ Active     |
| **Delhi Assembly** | 2025, 2020, 2015 | Delhi            | ✅ Active     |
| **Maharashtra**    | 2024, 2019       | Maharashtra      | ✅ Active     |
| **Other States**   | Various          | Generic Support  | 🔄 On Request |

</div>

### **📋 Output Data Structure**

Each scraper produces 4 JSON files:

#### **1. parties.json**

```json
[
    {
        "party_name": "Bharatiya Janata Party",
        "symbol": "Lotus",
        "total_seats": 240
    }
]
```

#### **2. constituencies.json**

```json
[
    {
        "constituency_id": "1",
        "constituency_name": "Constituency Name",
        "state_id": "DL"
    }
]
```

#### **3. candidates.json**

**Lok Sabha format:**

```json
[
    {
        "party_id": 369,
        "constituency": "Varanasi(77)",
        "candidate_name": "NARENDRA MODI",
        "votes": "612970",
        "margin": "152513"
    }
]
```

**Vidhan Sabha format:**

```json
[
    {
        "Constituency Code": "U051",
        "Name": "Candidate Name",
        "Party": "Party Name",
        "Status": "WON",
        "Votes": "12345",
        "Margin": "1234",
        "Image URL": "https://..."
    }
]
```

#### **4. Election Metadata (elections/\*.json)**

**Lok Sabha:**

```json
{
    "election_id": "lok-sabha-2024",
    "name": "Lok Sabha General Election 2024",
    "type": "LOK_SABHA",
    "year": 2024,
    "total_constituencies": 543,
    "total_candidates": 3802,
    "total_parties": 211,
    "result_status": "DECLARED",
    "winning_party_seats": 240
}
```

**Vidhan Sabha:**

```json
{
    "election_id": "DL_2025_ASSEMBLY",
    "name": "Delhi Assembly Election 2025",
    "type": "VIDHANSABHA",
    "year": 2025,
    "state_id": "DL",
    "state_name": "Delhi",
    "total_constituencies": 70,
    "total_candidates": 6914,
    "total_parties": 3,
    "result_status": "DECLARED",
    "winning_party_seats": 48,
    "runner_up_party": "Aam Aadmi Party",
    "runner_up_seats": 22
}
```

### **🚨 Important Notes**

-   **⏰ Respectful Scraping**: Built-in delays to avoid overwhelming ECI servers
-   **🔄 Data Updates**: Re-run scrapers to get latest results
-   **💾 Storage**: Large datasets may require significant disk space
-   **🌐 Internet Required**: Active internet connection needed for scraping
-   **📅 Election Timing**: Best results during and after election declaration

### **🐛 Troubleshooting Scraping**

```bash
# Common issues and solutions

# 1. Connection timeout
python scripts/scrape_all.py --year 2024  # Increase timeout in config

# 2. Missing dependencies
pip install -r requirements.txt

# 3. Permission errors
chmod +x scripts/scrape_all.py

# 4. Rate limiting
# Wait and retry - scrapers include automatic rate limiting

# 5. Incomplete data
# Check network connection and ECI website availability
```

---

## 🛠️ **Scripts & Services**

### **📋 Available Scripts**

Rajniti includes several utility scripts for database management, data processing, and maintenance tasks.

#### **Database Management Scripts**

##### **1. Database Management (`scripts/db.py`)**

Comprehensive database management utility:

```bash
# Sync database with models (auto-generate & run migrations)
python scripts/db.py sync

# Initialize database (create all tables)
python scripts/db.py init

# Migrate JSON data to database
python scripts/db.py migrate

# Preview migration without making changes
python scripts/db.py migrate --dry-run

# Reset database (⚠️ WARNING: deletes all data)
python scripts/db.py reset
```

**Prerequisites:**

-   `DATABASE_URL` environment variable must be set
-   PostgreSQL database must be running

**Usage Examples:**

```bash
# Setup new database
export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"
python scripts/db.py init
python scripts/db.py migrate

# Sync model changes
python scripts/db.py sync

# Preview what would be migrated
python scripts/db.py migrate --dry-run
```

##### **2. Database Sync (`scripts/sync_db.py`)**

Sync database schema with models:

```bash
# Sync database schema
python scripts/sync_db.py
```

##### **3. JSON to Database Migration (`scripts/migrations/migrate_json_to_db.py`)**

Migrate existing JSON data files to PostgreSQL:

```bash
# Migrate all JSON data to database
python scripts/migrations/migrate_json_to_db.py
```

#### **Data Processing Scripts**

##### **4. Candidate Data Population Agent (`scripts/run_candidate_agent.py`)**

AI-powered agent that populates detailed candidate information:

```bash
# Process 10 candidates with default settings
python scripts/run_candidate_agent.py

# Process 50 candidates with custom delays
python scripts/run_candidate_agent.py --batch-size 50 --delay-between-candidates 3.0

# Dry run to see which candidates would be processed
python scripts/run_candidate_agent.py --dry-run

# Process with specific LLM provider
python scripts/run_candidate_agent.py --provider openai --batch-size 20

# Process with custom delays
python scripts/run_candidate_agent.py \
  --batch-size 100 \
  --delay-between-candidates 3.0 \
  --delay-between-requests 3.0
```

**Options:**

-   `--batch-size`: Number of candidates to process (default: 10)
-   `--delay-between-candidates`: Delay in seconds between candidates (default: 2.0)
-   `--delay-between-requests`: Delay in seconds between API requests (default: 1.0)
-   `--provider`: LLM provider - `perplexity`, `openai` (default: perplexity)
-   `--dry-run`: Preview without making changes

**Prerequisites:**

-   `DATABASE_URL` environment variable
-   `PERPLEXITY_API_KEY`, `OPENAI_API_KEY` (depending on provider)

##### **5. Vector Database Sync (`scripts/sync_candidates_to_vector_db.py`)**

Sync candidate data to ChromaDB for semantic search:

```bash
# Sync all candidates
python scripts/sync_candidates_to_vector_db.py

# Sync with custom batch size
python scripts/sync_candidates_to_vector_db.py --batch-size 50

# Sync only winners
python scripts/sync_candidates_to_vector_db.py --winners-only

# Sync specific state
python scripts/sync_candidates_to_vector_db.py --state DL

# Sync with custom ChromaDB path
python scripts/sync_candidates_to_vector_db.py --chroma-db-path data/custom_chroma
```

**Options:**

-   `--batch-size`: Number of candidates to process per batch (default: 100)
-   `--winners-only`: Sync only winning candidates
-   `--state`: Sync only candidates from specific state (e.g., DL, MH)
-   `--chroma-db-path`: Custom path for ChromaDB storage

**Prerequisites:**

-   `DATABASE_URL` environment variable
-   ChromaDB will be created automatically if it doesn't exist

##### **6. Remove NOTA Candidates (`scripts/remove_nota_candidates.py`)**

Remove NOTA (None of the Above) entries from candidate data:

```bash
# Remove NOTA from Lok Sabha 2024 data
python scripts/remove_nota_candidates.py
```

**Note:** This script currently targets a specific file path. Modify the script to target different files if needed.

#### **Scraping Scripts**

See the [Data Scraping](#-data-scraping) section for detailed scraping script documentation.

**Quick Reference:**

```bash
# Interactive scraper (recommended)
python scripts/scrape_interactive.py

# Lok Sabha scraper
python scripts/scrape_lok_sabha.py --url <ECI_URL>

# Vidhan Sabha scraper
python scripts/scrape_vidhan_sabha.py --url <ECI_URL>
```

### **🚀 Running Services**

#### **1. Development Server**

Start the Flask development server:

```bash
# Using Make (recommended)
make dev

# Or directly
python run.py

# With custom host/port
FLASK_HOST=0.0.0.0 FLASK_PORT=8000 python run.py
```

**Environment Variables:**

-   `FLASK_HOST`: Server host (default: `0.0.0.0`)
-   `FLASK_PORT`: Server port (default: `8000`)
-   `FLASK_ENV`: Environment mode - `development` or `production` (default: `development`)
-   `FLASK_DEBUG`: Enable debug mode - `True` or `False` (default: `True`)

**Access Points:**

-   API: `http://localhost:8000/api/v1/`
-   Health Check: `http://localhost:8000/api/v1/health`
-   API Docs: `http://localhost:8000/api/v1/doc`

#### **2. Frontend Development Server**

Start the Next.js frontend:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

**Access Points:**

-   Frontend: `http://localhost:3000`

#### **3. Docker Services**

Run all services with Docker Compose:

```bash
# Start all services (API + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Stop and remove volumes
docker-compose down -v
```

**Services:**

-   **API**: `http://localhost:8000`
-   **PostgreSQL**: `localhost:5432`

#### **4. Database Service**

**Using Docker:**

```bash
# Stop container
docker stop rajniti-postgres

# Remove container
docker rm rajniti-postgres
```

**Using Local PostgreSQL:**

```bash
# Start PostgreSQL service (macOS)
brew services start postgresql

# Start PostgreSQL service (Linux)
sudo systemctl start postgresql

# Create database
createdb rajniti

# Connect to database
psql -d rajniti
```

### **📝 Make Commands**

Quick reference for common Make commands:

```bash
# Install, build, and start (all-in-one, uses pip-compile)
make

# Compile requirements.txt from requirements.in (pip-compile)
make compile

# Stop application
make stop

# Restart application
make restart

# View logs
make logs

# Clean up Docker resources
make clean

# Show help
make help
```

### **⚙️ Environment Setup**

Create a `.env` file in the project root:

```bash
# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=8000

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/rajniti

# AI Services (optional)
PERPLEXITY_API_KEY=your-perplexity-api-key
OPENAI_API_KEY=your-openai-api-key

# Vector Database (optional)
CHROMA_DB_PATH=data/chroma_db
```

### **🔍 Troubleshooting Scripts**

**Common Issues:**

1. **"Module not found" errors:**

    ```bash
    # Ensure virtual environment is activated
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

2. **Database connection errors:**

    ```bash
    # Check DATABASE_URL is set
    echo $DATABASE_URL

    # Verify PostgreSQL is running
    docker ps  # For Docker
    # or
    pg_isready  # For local PostgreSQL
    ```

3. **Permission errors:**

    ```bash
    # Make scripts executable
    chmod +x scripts/*.py
    ```

4. **API key errors:**
    ```bash
    # Verify API keys are set
    echo $PERPLEXITY_API_KEY
    echo $OPENAI_API_KEY
    ```

---

## 📚 **API Documentation**

### **🎯 API Overview**

-   **API Base URL**: `http://localhost:8000/api/v1/`
-   **Health Check**: `http://localhost:8000/api/v1/health`
-   **API Documentation**: `http://localhost:8000/api/v1/doc` (JSON format)
-   **API Root**: `http://localhost:8000/api/v1/` (lists all endpoints)

### **📖 Interactive API Documentation**

Access the complete API documentation programmatically:

```bash
# Get full API documentation in JSON format
curl http://localhost:8000/api/v1/doc

# Get API root with endpoint list
curl http://localhost:8000/api/v1/
```

The `/doc` endpoint returns a comprehensive JSON document with:

-   All available endpoints
-   Request/response formats
-   Query parameters
-   Example requests and responses
-   Status codes

### **🔥 Core Endpoints**

#### **Elections API**

| Endpoint                                         | Method | Description                    | Query Parameters   |
| ------------------------------------------------ | ------ | ------------------------------ | ------------------ |
| `/api/v1/elections`                              | GET    | Get all elections              | None               |
| `/api/v1/elections/{election-id}`                | GET    | Get election details           | None               |
| `/api/v1/elections/{election-id}/candidates`     | GET    | Get candidates by election     | `limit` (optional) |
| `/api/v1/elections/{election-id}/constituencies` | GET    | Get constituencies by election | None               |
| `/api/v1/elections/{election-id}/parties`        | GET    | Get parties by election        | None               |

**Example Requests:**

```bash
# Get all elections
curl "http://localhost:8000/api/v1/elections"

# Get Lok Sabha 2024 details
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024"

# Get candidates for an election (with limit)
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/candidates?limit=10"
```

#### **Candidates API**

| Endpoint                                                                      | Method | Description                    | Query Parameters                                             |
| ----------------------------------------------------------------------------- | ------ | ------------------------------ | ------------------------------------------------------------ |
| `/api/v1/candidates/search`                                                   | GET    | Search candidates by name      | `q` (required), `election_id` (optional), `limit` (optional) |
| `/api/v1/candidates/{candidate_id}`                                           | GET    | Get candidate by ID            | None                                                         |
| `/api/v1/candidates/winners`                                                  | GET    | Get all winning candidates     | `election_id` (optional)                                     |
| `/api/v1/candidates/party/{party_name}`                                       | GET    | Get candidates by party        | `election_id` (optional)                                     |
| `/api/v1/elections/{election_id}/candidates/{candidate_id}`                   | GET    | Get candidate details          | None                                                         |
| `/api/v1/elections/{election_id}/constituencies/{constituency_id}/candidates` | GET    | Get candidates by constituency | None                                                         |

**Example Requests:**

```bash
# Search for candidates named "Modi"
curl "http://localhost:8000/api/v1/candidates/search?q=modi"

# Search with election filter
curl "http://localhost:8000/api/v1/candidates/search?q=modi&election_id=lok-sabha-2024"

# Get candidate by ID
curl "http://localhost:8000/api/v1/candidates/12345"

# Get all winners
curl "http://localhost:8000/api/v1/candidates/winners"

# Get winners for specific election
curl "http://localhost:8000/api/v1/candidates/winners?election_id=lok-sabha-2024"

# Get candidates by party
curl "http://localhost:8000/api/v1/candidates/party/Bharatiya%20Janata%20Party"

# Get candidates in a constituency
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/constituencies/1/candidates"
```

#### **Constituencies API**

| Endpoint                                                                   | Method | Description                    | Query Parameters |
| -------------------------------------------------------------------------- | ------ | ------------------------------ | ---------------- |
| `/api/v1/elections/{election_id}/constituencies`                           | GET    | Get constituencies by election | None             |
| `/api/v1/elections/{election_id}/constituencies/{constituency_id}`         | GET    | Get constituency details       | None             |
| `/api/v1/elections/{election_id}/constituencies/{constituency_id}/results` | GET    | Get constituency results       | None             |
| `/api/v1/constituencies/state/{state_code}`                                | GET    | Get constituencies by state    | None             |

**Example Requests:**

```bash
# Get all constituencies for an election
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/constituencies"

# Get specific constituency
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/constituencies/1"

# Get constituency results
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/constituencies/1/results"

# Get constituencies by state
curl "http://localhost:8000/api/v1/constituencies/state/DL"
```

#### **Parties API**

| Endpoint                                               | Method | Description                   | Query Parameters         |
| ------------------------------------------------------ | ------ | ----------------------------- | ------------------------ |
| `/api/v1/parties`                                      | GET    | Get all parties               | None                     |
| `/api/v1/elections/{election_id}/parties`              | GET    | Get parties by election       | None                     |
| `/api/v1/elections/{election_id}/parties/{party_name}` | GET    | Get party details in election | None                     |
| `/api/v1/parties/{party_name}/performance`             | GET    | Get party performance         | `election_id` (optional) |

**Example Requests:**

```bash
# Get all parties
curl "http://localhost:8000/api/v1/parties"

# Get parties in an election
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/parties"

# Get specific party details
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/parties/Bharatiya%20Janata%20Party"

# Get party performance
curl "http://localhost:8000/api/v1/parties/Bharatiya%20Janata%20Party/performance"

# Get party performance for specific election
curl "http://localhost:8000/api/v1/parties/Bharatiya%20Janata%20Party/performance?election_id=lok-sabha-2024"
```

#### **Questions API (Vector Search)**

| Endpoint                                 | Method | Description                      | Request Body                                                                         |
| ---------------------------------------- | ------ | -------------------------------- | ------------------------------------------------------------------------------------ |
| `/api/v1/questions`                      | GET    | Get predefined questions         | None                                                                                 |
| `/api/v1/questions/ask`                  | POST   | Ask a question (semantic search) | `question` (required), `candidate_id` (optional), `n_results` (optional, default: 5) |
| `/api/v1/questions/{question_id}/answer` | GET    | Answer predefined question       | Query: `candidate_id` (optional), `n_results` (optional)                             |

**Example Requests:**

```bash
# Get predefined questions
curl "http://localhost:8000/api/v1/questions"

# Ask a question
curl -X POST "http://localhost:8000/api/v1/questions/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Who are the candidates with business background?", "n_results": 5}'

# Ask question about specific candidate
curl -X POST "http://localhost:8000/api/v1/questions/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the education background?", "candidate_id": "12345"}'

# Answer predefined question
curl "http://localhost:8000/api/v1/questions/1/answer?candidate_id=12345&n_results=5"
```

#### **User API**

| Endpoint                       | Method    | Description                 | Request Body                                                                                              |
| ------------------------------ | --------- | --------------------------- | --------------------------------------------------------------------------------------------------------- |
| `/api/v1/users/sync`           | POST      | Sync user from NextAuth     | `id`, `email` (required), `name`, `profile_picture` (optional)                                            |
| `/api/v1/users/{user_id}`      | GET       | Get user by ID              | None                                                                                                      |
| `/api/v1/users/{user_id}`      | PATCH/PUT | Update user profile         | `username`, `name`, `state`, `city`, `age_group`, `pincode`, `political_ideology`, `onboarding_completed` |
| `/api/v1/users/check-username` | POST      | Check username availability | `username` (required), `user_id` (optional)                                                               |

**Example Requests:**

```bash
# Sync user from NextAuth
curl -X POST "http://localhost:8000/api/v1/users/sync" \
  -H "Content-Type: application/json" \
  -d '{"id": "google_123", "email": "user@example.com", "name": "John Doe"}'

# Get user
curl "http://localhost:8000/api/v1/users/google_123"

# Update user profile
curl -X PATCH "http://localhost:8000/api/v1/users/google_123" \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "state": "DL", "city": "New Delhi"}'

# Check username availability
curl -X POST "http://localhost:8000/api/v1/users/check-username" \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe"}'
```

#### **Health & Root Endpoints**

| Endpoint         | Method | Description                       |
| ---------------- | ------ | --------------------------------- |
| `/api/v1/`       | GET    | API root with endpoint list       |
| `/api/v1/health` | GET    | Health check with database status |
| `/api/v1/doc`    | GET    | Complete API documentation (JSON) |

**Example Requests:**

```bash
# API root
curl "http://localhost:8000/api/v1/"

# Health check
curl "http://localhost:8000/api/v1/health"

# API documentation
curl "http://localhost:8000/api/v1/doc"
```

---

## 💡 **Usage Examples**

### **Basic Queries**

```bash
# Get all elections
curl "http://localhost:8000/api/v1/elections"

# Search for candidates named "Modi"
curl "http://localhost:8000/api/v1/candidates/search?q=modi"

# Get Lok Sabha 2024 winners
curl "http://localhost:8000/api/v1/elections/lok-sabha-2024/winners"

# Get all parties
curl "http://localhost:8000/api/v1/parties"
```

### **Filtering Examples**

```bash
# Get candidates by party
curl "http://localhost:8000/api/v1/candidates/party/Bharatiya%20Janata%20Party"

# Get constituency candidates
curl "http://localhost:8000/api/v1/elections/delhi-assembly-2025/constituencies/DL-1/candidates"

# Get party performance
curl "http://localhost:8000/api/v1/parties/Bharatiya%20Janata%20Party/performance"
```

### **Python Integration**

```python
import requests

# Simple API client
BASE_URL = "http://localhost:8000/api/v1"

# Search for candidates
response = requests.get(f"{BASE_URL}/candidates/search", params={"q": "modi"})
data = response.json()

if data['success']:
    for candidate in data['data']['candidates']:
        name = candidate.get('Name') or candidate.get('candidate_name', '')
        party = candidate.get('Party', '')
        print(f"{name} - {party}")

# Get election details
response = requests.get(f"{BASE_URL}/elections/lok-sabha-2024")
election = response.json()
print(f"Election: {election['data']['name']}")
print(f"Total candidates: {election['data']['statistics']['total_candidates']}")
```

---

## 🏗️ **Architecture**

```
rajniti/
├── app/
│   ├── controllers/            # 🎯 MVC Controllers (business logic)
│   ├── core/                   # 🔧 Simple utilities & exceptions
│   ├── data/                   # 📊 Election data (JSON files)
│   │   ├── lok_sabha/          # Lok Sabha election data
│   │   └── vidhan_sabha/       # Assembly election data
│   ├── models/                 # 📋 Pydantic models
│   ├── routes/                 # 🌐 Flask API routes
│   ├── services/               # 💾 Data access layer
│   └── __init__.py             # Flask app factory
├── tests/                      # Test files
├── requirements.in             # 📦 Direct dependencies
├── requirements.txt            # 📦 Compiled dependencies (pip-compile)
├── docker-compose.yml          # 🐳 Docker setup
├── dockerfile                  # 🐳 Container config
└── run.py                      # 🚀 Development server
```

---

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Application (minimal configuration)
SECRET_KEY=your-secret-key              # Flask secret key
FLASK_ENV=production                    # Environment (development/production)

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/rajniti  # PostgreSQL connection
# Perplexity AI API (for search functionality)
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

#### Common Errors

1. **"Perplexity API key not provided"**

    - Solution: Set `PERPLEXITY_API_KEY` environment variable or add to `.env` file

2. **"Module not found: perplexityai"**

    - Solution: Run `pip install -r requirements.txt`

3. **Rate limit exceeded**
    - Solution: Wait a moment and retry, or upgrade your Perplexity API plan

### **📚 Resources**

-   [Perplexity API Documentation](https://docs.perplexity.ai/)
-   [API Quickstart Guide](https://docs.perplexity.ai/guides/perplexity-sdk)
-   [Search API Guide](https://docs.perplexity.ai/guides/search-guide)
-   [Location Filter Guide](https://docs.perplexity.ai/guides/user-location-filter-guide)

---

## 🗄️ **Database**

Rajniti now includes PostgreSQL support for future data storage needs.

### **Setup with Docker**

```bash
# Start both API and PostgreSQL
docker-compose up -d

# PostgreSQL will be available at:
# - Host: localhost
# - Port: 5432
# - Database: rajniti
# - User: rajniti
# - Password: rajniti_dev_password
```

### **Local Development**

```bash
# Set DATABASE_URL in your environment
export DATABASE_URL="postgresql://rajniti:rajniti_dev_password@localhost:5432/rajniti"

# Start the app
python run.py
```

### **Database Health Check**

Check database connectivity via the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

Response with database connected:

```json
{
    "success": true,
    "message": "Rajniti API is healthy",
    "version": "1.0.0",
    "database": {
        "connected": true,
        "status": "healthy"
    }
}
```

**Note:** The application works perfectly fine without a database configured. Database support is optional and ready for future schema implementation.

## 🔍 **Perplexity AI Search Integration**

Rajniti integrates with Perplexity AI API to provide powerful, India-focused search capabilities for political information, election data, and news.

### **🚀 Quick Setup**

1. **Get Your API Key**

    - Sign up at [Perplexity AI](https://www.perplexity.ai/)
    - Navigate to API settings and generate your API key
    - Free tier available for testing

2. **Configure Environment**

    ```bash
    # Copy example env file
    cp .env.example .env

    # Edit .env and add your API key
    PERPLEXITY_API_KEY=your-actual-api-key-here
    ```

3. **Install Dependencies**
    ```bash
    # Install/update requirements
    pip install -r requirements.txt
    ```

### **✨ Features**

-   🇮🇳 **India-Focused**: Automatically filters search results for Indian context
-   🎯 **Region-Specific**: Support for state/city-level searches (e.g., Delhi, Maharashtra)
-   🔍 **Real-time Search**: Access latest political news and election information
-   🌐 **Web Search**: Leverages Perplexity's AI-powered web search
-   📚 **Citations**: Returns sources for all information
-   ⚡ **Fast & Reliable**: Built-in error handling and retries

### **💻 Usage Examples**

#### **Basic Python Usage**

```python
from app.services.perplexity_service import PerplexityService

# Initialize service (reads PERPLEXITY_API_KEY from environment)
service = PerplexityService()

# Simple search with India filter
results = service.search("Latest election results in India 2025")
print(results['answer'])
print(results['citations'])

# Region-specific search
results = service.search_india(
    query="political news today",
    region="Delhi",
    city="New Delhi"
)

# Multiple queries at once
queries = [
    "Lok Sabha election 2024 results",
    "Delhi Assembly election 2025 results"
]
results = service.search_multiple_queries(queries)
```

#### **Test the Integration**

Run the included test script to verify your setup:

```bash
# Set your API key
export PERPLEXITY_API_KEY='your-api-key-here'

# Run test script
python scripts/test_perplexity.py
```

Expected output:

```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
Perplexity API Integration Test
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

🔍 Testing Basic India Search...
✅ Perplexity service initialized successfully
📝 Query: Latest election results in India 2025
✅ Search completed successfully!
```

### **⚙️ Advanced Configuration**

#### **Custom Location Filters**

```python
# Specific location with coordinates
location = {
    "country": "IN",
    "region": "Maharashtra",
    "city": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777
}
results = service.search("local political events", location=location)
```

#### **Multiple Regions**

```python
# Search across different regions
regions = ["Delhi", "Maharashtra", "Karnataka"]
for region in regions:
    results = service.search_india(
        "election updates",
        region=region
    )
    print(f"{region}: {results['answer'][:200]}...")
```

### **🔌 API Models**

Perplexity supports different models:

-   **sonar**: Standard model, optimized for search (default, recommended)
-   **sonar-pro**: Advanced model with higher accuracy (requires pro plan)

### **📝 Response Format**

```python
{
    "query": "Your search query",
    "answer": "AI-generated answer based on search results",
    "citations": ["https://source1.com", "https://source2.com", ...],
    "model": "sonar",
    "location": {"country": "IN"}
}
```

### **🔐 Security Notes**

-   **Never commit** your API key to git
-   Use `.env` files for local development
-   Use environment variables for production deployment
-   The `.env.example` file shows the format but doesn't contain real keys

### **💡 Use Cases**

-   **Election Research**: Search for latest election results and analysis
-   **Political News**: Get India-focused political news and updates
-   **Candidate Information**: Research candidates across different elections
-   **Party Performance**: Analyze party performance in different regions
-   **Policy Updates**: Track government policy changes and announcements

### **🐛 Troubleshooting**

#### API Key Issues

```bash
# Check if API key is set
echo $PERPLEXITY_API_KEY

# Verify .env file exists and has correct format
cat .env | grep PERPLEXITY_API_KEY
```

#### Common Errors

1. **"Perplexity API key not provided"**

    - Solution: Set `PERPLEXITY_API_KEY` environment variable or add to `.env` file

2. **"Module not found: perplexityai"**

    - Solution: Run `pip install -r requirements.txt`

3. **Rate limit exceeded**
    - Solution: Wait a moment and retry, or upgrade your Perplexity API plan

### **📚 Resources**

-   [Perplexity API Documentation](https://docs.perplexity.ai/)
-   [API Quickstart Guide](https://docs.perplexity.ai/guides/perplexity-sdk)
-   [Search API Guide](https://docs.perplexity.ai/guides/search-guide)
-   [Location Filter Guide](https://docs.perplexity.ai/guides/user-location-filter-guide)

---

## 🤖 **Candidate Data Population Agent**

Rajniti includes an intelligent agent that automatically populates detailed candidate information using Perplexity AI. This agent fills in education background, political history, family details, and asset information for all candidates.

### **🚀 Quick Start**

1. **Prerequisites**

    ```bash
    # Ensure database is set up
    export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"

    # Ensure Perplexity API key is configured
    export PERPLEXITY_API_KEY="your-api-key-here"
    ```

2. **Run the Agent**

    ```bash
    # Process 10 candidates with default settings
    python scripts/run_candidate_agent.py

    # Process 50 candidates with custom delays
    python scripts/run_candidate_agent.py --batch-size 50 --delay-between-candidates 3.0

    # Dry run to see which candidates would be processed
    python scripts/run_candidate_agent.py --dry-run
    ```

### **✨ Features**

-   🔍 **Automatic Discovery**: Finds candidates with missing information
-   🤖 **AI-Powered**: Uses Perplexity AI for accurate data extraction
-   📊 **Structured Data**: Extracts data in well-defined JSON format
-   🔄 **Incremental Updates**: Processes candidates in batches
-   ⚡ **Smart Rate Limiting**: Built-in delays to respect API limits
-   📝 **Detailed Logging**: Comprehensive progress tracking
-   🛡️ **Error Handling**: Gracefully handles API failures

### **📚 Data Populated**

The agent populates four types of detailed information:

1. **Education Background**: Graduation year, field of study, college/school
2. **Political Background**: Electoral history with all contested elections
3. **Family Background**: Information about father, mother, spouse, and children
4. **Assets**: Commercial assets, cash assets, and bank details

### **💻 Usage Examples**

#### **Basic Usage**

```bash
# Process 10 candidates
python scripts/run_candidate_agent.py
```

#### **Large Batch Processing**

```bash
# Process 100 candidates with conservative delays
python scripts/run_candidate_agent.py \
  --batch-size 100 \
  --delay-between-candidates 3.0 \
  --delay-between-requests 3.0
```

#### **Programmatic Usage**

```python
from app.database.session import get_db_session
from app.services.candidate_agent import CandidateDataAgent

# Initialize agent
agent = CandidateDataAgent()

# Run with custom settings
with get_db_session() as session:
    stats = agent.run(
        session=session,
        batch_size=20,
        delay_between_candidates=2.0
    )

    print(f"Processed: {stats['total_processed']}")
    print(f"Successful: {stats['successful']}")
```

### **📖 Documentation**

For detailed documentation, see [docs/CANDIDATE_AGENT.md](docs/CANDIDATE_AGENT.md)

Topics covered:

-   Architecture and design
-   Data structures
-   Error handling
-   Best practices
-   Troubleshooting
-   Performance tuning

---

## 🔍 **Vector Database & Semantic Search**

Rajniti includes ChromaDB integration for semantic search across candidate information. This enables natural language queries to find candidates based on education, political history, assets, and more.

### **🚀 Quick Start**

#### **Automatic Sync**

Vector database automatically syncs when the candidate agent populates data:

```bash
# Auto-syncs to vector DB during data population
python scripts/run_candidate_agent.py --batch-size 10
```

#### **Manual Sync**

Use the sync script for periodic updates:

```bash
# Sync all candidates
python scripts/sync_candidates_to_vector_db.py

# Sync only winners
python scripts/sync_candidates_to_vector_db.py --winners-only

# Sync specific state
python scripts/sync_candidates_to_vector_db.py --state DL
```

### **✨ Features**

-   **Semantic Search**: Find candidates using natural language queries
-   **Auto-Sync**: Automatic synchronization after data population
-   **Batch Processing**: Efficient batch syncing with configurable size
-   **Filtering**: Sync by status, state, or candidate type
-   **Metadata**: Rich metadata for filtering and retrieval

### **💻 Programmatic Usage**

```python
from app.services.vector_db_service import VectorDBService

# Initialize service
vector_db = VectorDBService(collection_name="candidates")

# Query for similar candidates
results = vector_db.query_similar(
    "politician from Delhi with business background",
    n_results=5
)

for result in results:
    print(f"{result['metadata']['name']} - {result['distance']}")
```

### **⚙️ Configuration**

```bash
# Set ChromaDB storage path (optional)
export CHROMA_DB_PATH="data/chroma_db"

# Required for sync operations
export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"
```

### **📖 Documentation**

For detailed documentation, see [docs/VECTOR_DB.md](docs/VECTOR_DB.md)

Topics covered:

-   Architecture and components
-   Data storage format
-   Usage examples
-   Performance considerations
-   Monitoring and maintenance
-   Troubleshooting

---

## 🚢 **Deployment**

### **Docker Deployment**

```yaml
# docker-compose.yml
version: "3.8"
services:
    postgres:
        image: postgres:16-alpine
        environment:
            - POSTGRES_USER=${POSTGRES_USER}
        ports:
            - "5432:5432"
        volumes:
            - postgres_data:/var/lib/postgresql/data

    rajniti-api:
        build: .
        ports:
            - "8000:8000"
        environment:
            - FLASK_ENV=production
            - SECRET_KEY=${SECRET_KEY}
            - DATABASE_URL=postgresql://rajniti:rajniti_dev_password@postgres:5432/rajniti
        volumes:
            - ./app/data:/app/app/data:ro
        depends_on:
            - postgres

volumes:
    postgres_data:
```

```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### **Cloud Deployment**

#### **Heroku**

```bash
# Install Heroku CLI and login
heroku create your-rajniti-api
git push heroku main
```

#### **AWS/Digital Ocean**

```bash
# Build and push to container registry
docker build -t rajniti-api .
docker tag rajniti-api your-registry/rajniti-api
docker push your-registry/rajniti-api
```

---

## 🧪 **Testing & Development**

### **Dependency Management (pip-compile)**

```bash
# Install pip-tools
pip install pip-tools

# Add new dependency to requirements.in
echo "new-package==1.0.0" >> requirements.in

# Compile dependencies (generates requirements.txt)
pip-compile requirements.in

# Install compiled dependencies
pip install -r requirements.txt

# Upgrade all dependencies
pip-compile --upgrade requirements.in
```

**Why pip-compile?**
- ✅ Pins all transitive dependencies for reproducible builds
- ✅ Generates `requirements.txt` with exact versions
- ✅ Easy to update: just edit `requirements.in` and recompile
- ✅ Used automatically in `make` command
- ✅ Gracefully handles Python version mismatches

### **Running Tests**

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Format code
black app/
isort app/
flake8 app/
```

## 📈 **Performance & Scalability**

### **Performance Features**

-   **Fast Startup**: Minimal dependencies, quick boot time
-   **JSON Serving**: Direct file-based data serving
-   **Simple Search**: Basic filtering and search capabilities
-   **Memory Efficient**: Low memory footprint
-   **Stateless**: No database dependencies

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### **Development Setup**

```bash
# Fork and clone
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Create feature branch
git checkout -b feature/amazing-feature

# Install dependencies using pip-compile
pip install pip-tools
pip-sync requirements.txt

# Make your changes and test
pytest tests/

# Submit pull request
git push origin feature/amazing-feature
```

### **Contribution Guidelines**

-   🐛 **Bug Reports**: Use GitHub issues with detailed descriptions
-   ✨ **Feature Requests**: Discuss in issues before implementing
-   📝 **Documentation**: Update docs for any API changes
-   ✅ **Testing**: Ensure tests pass and add new tests
-   🎨 **Code Style**: Follow Black formatting and PEP 8

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

-   **Election Commission of India** for providing comprehensive election data
-   **Flask Community** for the excellent web framework
-   **Contributors** who helped make this project possible

---

## 📞 **Support & Community**

<div align="center">

[![GitHub Issues](https://img.shields.io/badge/Issues-GitHub-red.svg)](https://github.com/your-username/rajniti/issues)
[![Discussions](https://img.shields.io/badge/Discussions-GitHub-blue.svg)](https://github.com/your-username/rajniti/discussions)
[![Email](https://img.shields.io/badge/Email-Contact-green.svg)](mailto:rajniti@example.com)

**⭐ Star this repository if you find it helpful!**

</div>

---

<div align="center">

**Building with ❤️ for 🇮🇳 Democracy**

_Empowering citizens, researchers, and developers with accessible election data_

</div>
