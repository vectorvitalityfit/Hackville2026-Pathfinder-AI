# 🌐 ngrok Setup for Remote Access

## Why ngrok?
Browsers require **HTTPS** for camera/microphone access. ngrok gives you a secure HTTPS URL that works from anywhere!

---

## 🚀 Quick Setup

### Step 1: Install ngrok

**Download**: https://ngrok.com/download

**Or use Chocolatey** (Windows):
```powershell
choco install ngrok
```

### Step 2: Sign up (Free)

1. Go to: https://dashboard.ngrok.com/signup
2. Create free account
3. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken

### Step 3: Configure ngrok

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN
```
Replace `YOUR_AUTH_TOKEN` with the token from ngrok dashboard

---

## 🎯 Running with ngrok

### Terminal 1: Start Server (Backend + Frontend)
```powershell
.\start_server.ps1
```
(Run this from the `backend` directory)

### Terminal 2: Start ngrok
```powershell
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

### Step 4: Open on Phone

Copy the **https** URL (e.g., `https://abc123.ngrok-free.app`)

Open it on your phone - works from **anywhere** (not just same WiFi)!

---

## ✨ Benefits

✅ **HTTPS** - Camera/microphone will work
✅ **Anywhere** - Works on cellular data, different WiFi
✅ **No firewall issues** - No need to configure ports
✅ **Public URL** - Share with testers

---

## 📱 Full Workflow

```powershell
# Terminal 1: Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: ngrok
ngrok http 8000

# Phone: Open the https URL shown by ngrok
# Example: https://abc123.ngrok-free.app
```

---

## ⚠️ Important Notes

1. **Free tier limits**:
   - URL changes each restart
   - 1 user at a time
   - Request limits (~40 requests/min)

2. **ngrok warning page**:
   - First time you'll see ngrok warning
   - Click "Visit Site" to continue
   - This is normal for free tier

3. **Keep terminals open**:
   - Both backend and ngrok must stay running
   - If you close ngrok, URL stops working

---

## 🔒 Security

**Free tier is public** - anyone with URL can access

For production:
- Use ngrok paid plan (password protection)
- Or use Tailscale (private network)
- Or deploy to cloud (Render, Railway, etc.)

---

## 🎬 Ready!

Once ngrok shows the HTTPS URL:
- Open on phone browser
- Camera/microphone permissions will work
- Voice navigation fully functional!

---

## 💡 Pro Tips

**Custom subdomain** (ngrok paid):
```powershell
ngrok http --subdomain=myvoicenav 8000
# Always same URL: https://myvoicenav.ngrok.io
```

**ngrok dashboard**:
- Go to: http://localhost:4040
- See all requests in real-time
- Debug issues

**Keep URL persistent**:
- ngrok paid plan: Reserved domains
- Or use Cloudflare Tunnel (free alternative)

---

That's it! The HTTPS URL from ngrok will let camera/microphone work perfectly! 🎉
