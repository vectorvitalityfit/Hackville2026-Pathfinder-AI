# 📱 Web UI Mobile Setup

## 🌐 Access from Phone Browser - No Apps Needed!

### Step 1: Start the Backend

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

⚠️ **Important**: Use `0.0.0.0` not `127.0.0.1` so phone can connect!

### Step 2: Find Your PC's IP Address

**Windows**:
```powershell
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., `192.168.1.100`)

**OR Use PowerShell**:
```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*'}).IPAddress
```

### Step 3: Open on Phone

1. **Connect phone to same WiFi as PC**
2. **Open browser on phone** (Chrome/Safari)
3. **Go to**: `http://192.168.1.100:8000`
   - Replace `192.168.1.100` with YOUR PC's IP
4. **Allow camera and microphone** when prompted

### Step 4: Use the App

- **Tap 🎤 Speak** button
- **Say your command** (records for 3 seconds)
- **Listen to response** via phone speaker
- **Camera uses phone's rear camera** automatically

---

## ✨ Features

✅ Uses phone's camera directly (no IP Webcam app!)
✅ Voice input via phone microphone
✅ Audio output via phone speaker
✅ Full-screen immersive interface
✅ Works on iOS and Android
✅ No installation needed

---

## 🎯 Commands You Can Say

| Say This | What Happens |
|----------|--------------|
| "What's around me?" | Describes surroundings |
| "What's ahead?" | Checks forward path |
| "Is it safe?" | Safety check |
| "Take me to cafeteria" | Starts navigation |

---

## 🔧 Troubleshooting

### Can't connect from phone

**Check same WiFi**: Phone and PC must be on same network

**Windows Firewall**:
```powershell
# Allow port 8000
New-NetFirewallRule -DisplayName "Voice Nav" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Test connection**:
- Open `http://YOUR_PC_IP:8000` on PC first
- Should see the web interface
- Then try from phone

### Camera/microphone not working

- Browser must be HTTPS or localhost (use ngrok for HTTPS)
- Grant permissions when prompted
- Try Chrome browser (best compatibility)

### Audio not playing

- Check phone volume
- Try headphones
- Some browsers block autoplay - tap screen first

---

## 🚀 Quick Start Commands

```powershell
# Terminal 1: Start backend with network access
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Find your IP
ipconfig

# On phone: Open browser, go to:
# http://YOUR_PC_IP:8000
```

---

## 💡 Pro Tips

1. **Add to Home Screen** (iOS/Android)
   - Browser menu → Add to Home Screen
   - Works like a native app!

2. **Guided Access** (iOS)
   - Settings → Accessibility → Guided Access
   - Locks phone to the app

3. **Battery Saver**
   - Lower screen brightness
   - Use power bank
   - ~3-4 hours continuous use

4. **Better Audio**
   - Use Bluetooth headset
   - Or wired earphones
   - Clearer voice output

---

## 🔒 Security Note

This exposes your PC on local network. Only use on trusted WiFi!

For public use, add authentication or use ngrok/Tailscale.

---

**That's it!** Just start the backend and open in phone browser. No apps, no setup! 🎉
