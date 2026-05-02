# ⚡ AKSHU SERVER

**Secure Lua Script Server with XOR Encryption**

Built for Render.com deployment with GitHub integration.

---

## 🔐 Admin Credentials

| Field    | Value     |
|----------|-----------|
| Username | `akshu`   |
| Password | `akshu123`|

---

## 📁 Project Structure

```
akshu-server/
├── app.py                 # Main Flask server
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── README.md             # This file
├── data/                 # Data storage (auto-created)
│   ├── keys.json         # XOR keys database
│   └── scripts.json      # Scripts database
├── scripts/              # Script files (auto-created)
│   └── *.lua            # Stored Lua scripts
└── templates/            # HTML templates
    ├── index.html        # Home page
    ├── login.html        # Admin login
    └── dashboard.html    # Admin panel
```

---

## 🚀 How to Upload to GitHub & Deploy on Render

### Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and login
2. Click **"+"** → **"New repository"**
3. Name: `akshu-server`
4. Make it **Public** or **Private**
5. Click **"Create repository"**

### Step 2: Upload Files to GitHub

**Option A: Using Git Command Line**

```bash
# Open terminal in the project folder
cd akshu-server

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Akshu Server"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/akshu-server.git

# Push
git branch -M main
git push -u origin main
```

**Option B: Using GitHub Web Interface**

1. Open your new repository on GitHub
2. Click **"uploading an existing file"**
3. Drag & drop all files from the `akshu-server` folder
4. Click **"Commit changes"**

### Step 3: Deploy on Render

1. Go to [render.com](https://render.com) and login/signup
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub** account
4. Select the `akshu-server` repository
5. Configure:
   - **Name**: `akshu-server`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click **"Create Web Service"**
7. Wait for deployment (2-3 minutes)
8. Your server is live! 🎉

---

## 🔧 API Endpoints

### Public Endpoints (No Login Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Server health check |
| GET    | `/api/scripts/public` | List all scripts (no code) |
| POST   | `/api/validate-key` | Validate a key |
| POST   | `/api/run/<script_id>` | Execute script with key |

### Admin Endpoints (Login Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/login` | Admin login |
| GET    | `/dashboard` | Admin panel |
| GET    | `/api/keys` | List all keys |
| POST   | `/api/keys` | Create new key |
| DELETE | `/api/keys/<id>` | Delete key |
| GET    | `/api/scripts` | List all scripts |
| POST   | `/api/scripts` | Create new script |
| DELETE | `/api/scripts/<id>` | Delete script |

---

## 🛡️ XOR Encryption Flow

```
1. Admin creates XOR Key in Dashboard
2. Admin creates Script + selects Key
3. Script gets encrypted with XOR Key on server
4. Client sends POST to /api/run/<id> with key
5. Server validates key → decrypts → returns script
6. Script runs with real code!
```

---

## 📡 Example API Usage

### Validate Key
```bash
curl -X POST https://your-app.onrender.com/api/validate-key   -H "Content-Type: application/json"   -d '{"key": "AkshuSecret2026"}'
```

### Run Script
```bash
curl -X POST https://your-app.onrender.com/api/run/abc123   -H "Content-Type: application/json"   -d '{"key": "AkshuSecret2026"}'
```

---

## ⚠️ Important Notes

- **Data Persistence**: Keys and scripts are saved in JSON files. On Render free tier, filesystem resets on restart. For production, use a database.
- **Security**: Change default password in production by modifying `ADMIN_PASSWORD_HASH` in `app.py`.
- **XOR Key**: Never share your XOR key publicly. It's the only way to decrypt scripts.

---

## 👤 Made by Akshu

**Server Name**: Akshu Server v1.0  
**Features**: XOR Encryption | Key Validation | Script Storage | Admin Panel

---
