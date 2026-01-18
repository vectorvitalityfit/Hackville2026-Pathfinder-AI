# Voice Navigation - Quick Start Guide

## ✅ Setup Complete!

Your frontend is now configured to work with your backend API.

## 🚀 Running the Application

### Option 1: Development Mode (Recommended for Testing)

**Terminal 1 - Backend:**
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd static
npm run dev
```

**Terminal 3 - Expose (for mobile testing):**
```powershell
ngrok http 8080
```

Access at: `http://localhost:8080` or use ngrok URL

---

### Option 2: Production Build (Single Server)

**Build frontend:**
```powershell
cd static
npm run build
cd ..
```

**Run backend (serves both):**
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expose:**
```powershell
ngrok http 8000
```

Access at: `http://localhost:8000` or use ngrok URL

---

## 🎯 Features Available

### Navigation Commands
- "Navigate to [destination]" - Start walking navigation
- "Where am I?" - Get current location description
- "What's around me?" - Describe surroundings
- "Stop navigation" - End navigation mode

### Real-Time Obstacle Detection
Once navigation starts:
- Scans every 2 seconds
- Warns: "Chair ahead, move left"
- Warns: "Object on right, move left"
- Confirms: "Path clear"

### How It Works
1. Go to `/assist` page
2. Say "Start Assistance" or tap button
3. Camera and mic activate
4. Speak commands
5. System guides you continuously

## 📱 Mobile Testing

1. Start backend: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Start ngrok: `ngrok http 8000`
3. Open ngrok URL on phone
4. Grant camera/mic permissions
5. Navigate to `/assist`
6. Start speaking commands!

## 🔧 Configuration

API endpoint is configured in:
- `static/src/lib/api.ts` - API client
- `static/.env` - Environment variables (optional)
- `static/vite.config.ts` - Dev proxy settings

Default: Uses same origin (works with ngrok!)

## 🎤 Available Voice Commands

From your backend routes:
- Navigation: "Take me to [place]", "Navigate to [place]"
- Queries: "What do you see", "Describe this", "What's here"
- Control: "Stop", "Help", "Status"

Check `routes/command.py` for full command list!
