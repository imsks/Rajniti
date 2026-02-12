# 🚀 Quick Setup Guide - Rajniti

## Problem: API Connection Error

Your frontend is trying to connect to the backend API at `http://localhost:8000`, but the backend server is not running.

## Solution: Start the Backend Server

### Step 1: Install Python Dependencies

Your network has a web filter blocking PyPI. You have two options:

#### Option A: Use VPN or Different Network
```bash
cd "c:\Users\Krish Kumar\OneDrive\Desktop\rajniti\Rajniti"
pip install python-dotenv flask flask-cors sqlalchemy psycopg2-binary chromadb
```

#### Option B: Offline Installation (if you have the packages)
If you have the wheel files or can download them on another computer:
```bash
pip install --no-index --find-links=/path/to/packages -r requirements.txt
```

### Step 2: Start the Backend Server
```bash
cd "c:\Users\Krish Kumar\OneDrive\Desktop\rajniti\Rajniti"
python run.py
```

You should see output like:
```
2026-02-12 10:00:00 - rajniti.server - INFO - Starting Rajniti development server on 0.0.0.0:8000
2026-02-12 10:00:00 - rajniti.server - INFO - Debug mode: True, Environment: development
```

### Step 3: Verify Backend is Running

Open your browser and visit:
- **Health Check**: http://localhost:8000/api/v1/health
- **API Docs**: http://localhost:8000

### Step 4: Refresh Frontend

Once the backend is running, go back to your frontend at http://localhost:3001 and click "Try Again"

## Current Status

✅ Frontend running on http://localhost:3001  
❌ Backend NOT running (needs to be on http://localhost:8000)  
✅ .env file created with default settings  
❌ Python dependencies not installed (network filter blocking)

## Network Issue

Your network appears to have a web filter at `192.168.3.1:8090` that's blocking access to `files.pythonhosted.org`. 

**Solutions:**
1. Connect to a different network (home wifi, mobile hotspot)
2. Use a VPN
3. Ask network admin to whitelist `pypi.org` and `files.pythonhosted.org`
4. Download packages offline and install manually

## Alternative: Work on Frontend Only

For now, you can continue working on frontend styling and UI without the backend. The error page shows helpful instructions to users about starting the backend.
