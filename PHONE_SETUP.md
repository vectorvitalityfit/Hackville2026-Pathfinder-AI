# 📱 Phone Camera Setup Guide

## Option 1: Using Phone as Camera (IP Webcam)

### What You Need:
- ✅ Android phone with camera
- ✅ PC with this project installed
- ✅ Both devices on same WiFi network
- ✅ Bluetooth headset (for hands-free operation)

---

## 📋 Step-by-Step Setup

### Step 1: Install IP Webcam on Phone

1. **Download IP Webcam** (Android)
   - Open Google Play Store
   - Search for "IP Webcam" by Pavel Khlebovich
   - Install the app (it's free)

2. **Configure IP Webcam**
   - Open the app
   - Scroll to bottom
   - Tap **"Start server"**
   - Note the URL shown (e.g., `http://192.168.1.105:8080`)

3. **Mount Phone**
   - Attach phone to your chest/shoulder with mount or clip
   - Camera should face forward (your walking direction)
   - Keep phone screen on or use "Keep screen on" in IP Webcam settings

---

### Step 2: Find Your Phone's IP Address

**Method 1: From IP Webcam App**
- When server starts, URL is displayed at top
- Example: `http://192.168.1.105:8080`
- Write down this URL

**Method 2: From Phone Settings**
- Settings → WiFi → Connected network → Advanced
- Look for "IP address"
- Note the numbers (e.g., `192.168.1.105`)

---

### Step 3: Update Client Configuration

1. **Open client_orchestrator.py**

2. **Find this line** (around line 18):
   ```python
   CAMERA_URL = 0
   ```

3. **Replace with your phone's URL**:
   ```python
   CAMERA_URL = "http://192.168.1.105:8080/video"
   ```
   ⚠️ Replace `192.168.1.105` with YOUR phone's IP address
   ⚠️ Keep `/video` at the end

4. **Save the file**

---

### Step 4: Test Camera Connection

1. **Start backend**:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

2. **In another terminal, test camera**:
   ```powershell
   python client_orchestrator.py
   ```

3. **Look for**:
   ```
   📷 connecting to camera: http://192.168.1.105:8080/video ...
   🤖 Hello. I'm here to guide you.
   ```

4. **If you see errors**:
   - Check phone and PC are on same WiFi
   - Verify IP address is correct
   - Make sure IP Webcam server is running on phone
   - Try opening `http://192.168.1.105:8080` in PC browser (should show camera feed)

---

### Step 5: Connect Bluetooth Headset

1. **Pair headset with PC**:
   - Settings → Bluetooth → Add device
   - Put headset in pairing mode
   - Select headset from list

2. **Set as default audio device**:
   - Right-click speaker icon in taskbar
   - Sound settings → Output → Select headset
   - Sound settings → Input → Select headset microphone

3. **Test microphone**:
   - Sound settings → Input → Test microphone
   - Speak and watch the level bar

---

### Step 6: Run the System

1. **Start backend** (Terminal 1):
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

2. **Start client** (Terminal 2):
   ```powershell
   python client_orchestrator.py
   ```

3. **Wait for greeting**:
   - You should hear: "Hello. I'm here to guide you."

4. **Press Enter to speak**:
   - Press Enter key
   - Wait for "🎤 Recording..."
   - Speak your command (3 seconds)
   - System processes and responds

---

## 🎯 Usage Commands

Once running, press **Enter** then speak:

| Command | What It Does | Example Response |
|---------|-------------|------------------|
| "What's around me?" | Describes surroundings | "Hallway. Tables on right. Path clear." |
| "What's ahead?" | Checks forward path | "Clear path ahead. No obstacles." |
| "Is it safe?" | Safety check | "Path is clear. Safe to walk." |
| "Take me to cafeteria" | Start navigation | "Going to cafeteria. Follow me." |

---

## 🔧 Troubleshooting

### Problem: Can't connect to phone camera

**Solution 1: Check same WiFi**
```powershell
# On PC, check IP address
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
# Should start with same numbers as phone (e.g., both 192.168.1.X)
```

**Solution 2: Test in browser**
- Open browser on PC
- Go to: `http://192.168.1.105:8080`
- You should see camera interface
- If not, phone and PC aren't on same network

**Solution 3: Disable firewall temporarily**
```powershell
# Windows Firewall might block connection
# Test by temporarily disabling (Settings → Windows Security → Firewall)
```

### Problem: Audio not working

**Check microphone**:
```powershell
# List audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

**Fix**: Make sure headset is selected as default device in Windows sound settings

### Problem: Camera is upside down

**Fix in IP Webcam app**:
- Settings → Video orientation → Rotate 180°

### Problem: Poor camera quality

**Fix in IP Webcam app**:
- Settings → Video resolution → Select 640x480 or 1280x720
- Settings → Quality → 70-80%
- Settings → FPS limit → 15-20 fps

### Problem: Phone battery draining fast

**Solutions**:
- Keep phone plugged into power bank
- Lower video resolution in IP Webcam settings
- Reduce FPS to 10-15
- Disable audio streaming in IP Webcam (not needed)

---

## 📊 Network Requirements

**Bandwidth needed**:
- Video stream: ~1-2 Mbps
- Audio TTS: ~50 Kbps
- API calls: ~10 Kbps
- **Total: ~2 Mbps** (works on most home WiFi)

**Latency**:
- Same WiFi: 10-50ms ✅ Good
- Different WiFi/mobile data: 100-500ms ⚠️ May be laggy

---

## 🎒 Physical Setup Tips

### Phone Mounting Options:

1. **Chest Mount** (Best for walking)
   - GoPro chest harness + phone adapter
   - Amazon: "Action Camera Chest Mount"
   - Keeps hands free, stable footage

2. **Neck Lanyard** (Cheap option)
   - Phone lanyard with card holder
   - Let phone hang at chest level
   - Adjust camera angle

3. **Shirt Pocket** (Simplest)
   - Large shirt pocket
   - Camera lens facing out
   - May shift while walking

4. **Shoulder Strap**
   - Camera strap + phone clip
   - Over shoulder, phone at chest
   - Very stable

### Battery Solution:
- Portable power bank in pocket
- USB cable to phone
- 10,000mAh = ~4 hours runtime

---

## 🚀 Advanced: Remote Access

If you want to access from anywhere (not just local WiFi):

### Option A: ngrok (Quick)

1. **Install ngrok**: https://ngrok.com/download

2. **Expose backend**:
   ```powershell
   ngrok http 8000
   ```

3. **Update BACKEND_URL** in client_orchestrator.py:
   ```python
   BACKEND_URL = "https://abc123.ngrok.io"
   ```

### Option B: Tailscale (Secure)

1. **Install Tailscale** on PC and phone
2. Both devices get virtual IPs (e.g., `100.x.x.x`)
3. Use Tailscale IP instead of local IP
4. Works anywhere with internet

---

## 📱 Testing Checklist

Before going mobile, test everything:

- [ ] Phone camera connects successfully
- [ ] Video feed displays in browser at `http://PHONE_IP:8080`
- [ ] Backend responds at `http://localhost:8000/`
- [ ] Client can capture frames from phone camera
- [ ] Voice recording works via headset
- [ ] Text-to-speech plays through headset
- [ ] Can press Enter to trigger voice input
- [ ] All API calls complete (vision, brain, speech)
- [ ] Phone is securely mounted
- [ ] Phone is charging (power bank)
- [ ] Headset battery is charged

---

## 🎬 Ready to Go!

Once everything is working:

1. Mount phone on chest/shoulder
2. Put on Bluetooth headset
3. Start backend and client
4. Keep PC nearby or in backpack
5. Press Enter (or use remote button if headset has one)
6. Speak your command
7. Follow the assistant's voice guidance!

---

## 💡 Pro Tips

1. **Battery Life**: Phone + power bank = 4-6 hours
2. **Headset**: Get one with physical button to trigger recording
3. **Lighting**: System works best in well-lit environments
4. **Walking Speed**: Walk at normal pace, system processes every 2 seconds
5. **Emergency**: Keep sighted guide nearby for first tests
6. **Practice**: Test in safe, familiar environment first

---

**Need help?** Check the terminal output for debug messages or errors.
