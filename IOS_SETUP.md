# 📱 iOS Phone Camera Setup Guide

## Option 1A: Using iPhone as Camera

### What You Need:
- ✅ iPhone (iOS 12+)
- ✅ PC with this project installed
- ✅ Both devices on same WiFi network
- ✅ Bluetooth headset (for hands-free operation)

---

## 📋 iOS Camera App Options

### Recommended: WebCamera (Free)

1. **Download WebCamera**
   - Open App Store
   - Search "WebCamera - Connect Devices"
   - Install (free version works)

2. **Start Server**
   - Open WebCamera app
   - Tap the big **Play** button
   - Note the URL shown (e.g., `http://192.168.1.105:8080`)
   - Keep app open and screen on

3. **Find Video Stream URL**
   - The app shows: `http://192.168.1.105:8080`
   - For our system, use: `http://192.168.1.105:8080/video`

---

### Alternative 1: EpocCam (Recommended for Quality)

**Pros**: Better quality, wireless or USB
**Cons**: Free version has watermark

1. **Install EpocCam**
   - App Store: "EpocCam Webcam for Mac and PC"
   - Install on iPhone

2. **Install EpocCam Drivers on PC**
   - Download from: https://www.kinoni.com/
   - Install Windows drivers
   - Restart PC

3. **Connect**
   - Open EpocCam on iPhone
   - App auto-detects PC on same WiFi
   - On PC, EpocCam appears as virtual webcam

4. **Update Configuration**
   ```python
   # In client_orchestrator.py, use webcam index
   CAMERA_URL = 1  # or 2, depends on your system
   ```

---

### Alternative 2: iVCam (Good Quality)

**Pros**: High quality, low latency
**Cons**: Requires PC software

1. **Install iVCam**
   - App Store: "iVCam Webcam"
   - PC: Download from https://www.e2esoft.com/ivcam/

2. **Setup**
   - Install PC software
   - Open iVCam on iPhone
   - Connects automatically via WiFi

3. **Configuration**
   ```python
   # In client_orchestrator.py
   CAMERA_URL = 1  # iVCam appears as virtual webcam
   ```

---

### Alternative 3: Iriun Webcam (Simplest)

**Pros**: No ads, simple setup
**Cons**: Requires PC software

1. **Install Iriun**
   - App Store: "Iriun Webcam for PC and Mac"
   - PC: Download from https://iriun.com/

2. **Setup**
   - Install PC client
   - Open Iriun on iPhone
   - Auto-connects

3. **Configuration**
   ```python
   CAMERA_URL = 1  # Virtual webcam
   ```

---

## 🔧 Setup Instructions (WebCamera Method)

### Step 1: Install WebCamera on iPhone

1. Open App Store
2. Search "WebCamera"
3. Install the app with icon showing a camera
4. Open app and allow camera permissions

### Step 2: Start Camera Server

1. In WebCamera app, tap **Play** button
2. Note the IP address shown (e.g., `192.168.1.105:8080`)
3. Keep the app open (don't lock phone or switch apps)
4. Optional: Enable "Keep screen on" in app settings

### Step 3: Find Your iPhone's IP

**From WebCamera App**:
- URL is displayed when server starts
- Example: `http://192.168.1.105:8080`

**From iPhone Settings**:
- Settings → WiFi → (i) icon next to connected network
- Look for "IP Address"
- Note the numbers

### Step 4: Update Configuration

**Option A: Use setup script**
```powershell
.\setup_phone_camera.bat
# Enter iPhone IP when prompted
```

**Option B: Manual update**

Open `client_orchestrator.py` and change:
```python
CAMERA_URL = 0
```
to:
```python
CAMERA_URL = "http://192.168.1.105:8080/video"
```
*(Replace IP with your iPhone's IP)*

### Step 5: Test Connection

1. **Test in browser first**:
   - Open browser on PC
   - Go to: `http://192.168.1.105:8080`
   - You should see camera controls
   - Click "View stream" or similar to see video

2. **Test with system**:
   ```powershell
   python client_orchestrator.py
   ```
   - Should see: "📷 connecting to camera..."
   - Should NOT see: "Error: Could not open camera"

---

## 🎯 Virtual Webcam Method (EpocCam/iVCam/Iriun)

If using apps that create virtual webcams:

### Find the Camera Index

```powershell
# Run this to list all cameras
python -c "import cv2; [print(f'Index {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
```

Output example:
```
Index 0: True   <- Built-in laptop camera
Index 1: True   <- EpocCam/iVCam (your iPhone)
Index 2: False
```

### Update Configuration

```python
# In client_orchestrator.py
CAMERA_URL = 1  # Use the index where True appears
```

---

## 📱 Physical Setup (iPhone)

### Mounting Options:

1. **Phone Armband** (Chest level)
   - Running armband worn on chest
   - Camera faces forward
   - ~$15 on Amazon

2. **Lanyard with Card Holder**
   - Phone hangs at chest
   - Camera lens exposed
   - ~$10

3. **Clip-on Mount**
   - Clips to shirt pocket or collar
   - Adjustable angle
   - ~$12

4. **Action Camera Chest Mount**
   - GoPro chest harness + phone adapter
   - Very stable
   - ~$25

### Battery Solutions:
- Lightning power bank in pocket
- MagSafe battery pack (iPhone 12+)
- 10,000mAh = ~3-4 hours continuous

---

## 🔧 Troubleshooting iOS

### Problem: Can't connect to iPhone camera

**Check WiFi**:
```powershell
# PC and iPhone must be on SAME WiFi (not guest network)
ipconfig
# Look for IPv4 Address, should match iPhone (e.g., both 192.168.1.X)
```

**Disable WiFi Isolation**:
- Some routers have "AP Isolation" or "Client Isolation"
- This prevents devices from seeing each other
- Check router settings and disable it

**iOS Low Power Mode**:
- Settings → Battery → Low Power Mode → OFF
- Low Power Mode can disconnect camera apps

### Problem: Stream is laggy

**WebCamera Settings**:
- In app: Settings → Resolution → 640x480 (lower is faster)
- Settings → Frame Rate → 15 fps
- Settings → Quality → 60-70%

**Network**:
- Move closer to WiFi router
- Reduce other WiFi usage
- Use 5GHz WiFi if available

### Problem: App disconnects when screen locks

**Keep Screen On**:
- WebCamera: Settings → Keep screen awake → ON
- iOS: Settings → Display → Auto-Lock → Never (while using)
- Use Guided Access to lock iPhone to camera app

**Guided Access (Prevent accidental exit)**:
1. Settings → Accessibility → Guided Access → ON
2. Open camera app
3. Triple-click side button
4. Tap "Start"
5. Now iPhone is locked to camera app

### Problem: Camera orientation is wrong

**Fix in App**:
- WebCamera: Settings → Orientation → Landscape/Portrait
- Or rotate phone physically in mount

**Fix in OpenCV** (if needed):
Add to client_orchestrator.py:
```python
def capture_and_encode_frame(cap):
    ret, frame = cap.read()
    if not ret:
        return None
    
    # Rotate if needed
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    frame = cv2.resize(frame, (640, 480))
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()
```

---

## 🌐 URL Formats by App

| App | Stream URL Format |
|-----|-------------------|
| WebCamera | `http://IP:8080/video` |
| IP Webcam (Android) | `http://IP:8080/video` |
| EpocCam | Use camera index (e.g., `CAMERA_URL = 1`) |
| iVCam | Use camera index (e.g., `CAMERA_URL = 1`) |
| Iriun | Use camera index (e.g., `CAMERA_URL = 1`) |

---

## 💡 iOS-Specific Tips

1. **Battery**: iOS drains faster than Android
   - Use MagSafe battery pack
   - Or keep lightning cable connected to power bank

2. **Notifications**: Disable to prevent interruptions
   - Settings → Focus → Do Not Disturb → ON

3. **Calls**: Forward calls or enable airplane mode + WiFi
   - Settings → Airplane Mode → ON
   - Then turn WiFi back ON

4. **Background Refresh**: Keep camera app active
   - Don't switch apps
   - Use Guided Access to lock to camera

5. **iCloud Photos**: May interfere
   - Disable while using camera
   - Settings → Photos → iCloud Photos → OFF (temporary)

---

## 🚀 Quick Start (iOS Summary)

### Method 1: WebCamera App (Wireless)
1. Install WebCamera from App Store
2. Start server, note IP
3. Update: `CAMERA_URL = "http://IP:8080/video"`
4. Run system

### Method 2: EpocCam/iVCam (Better Quality)
1. Install app on iPhone + PC drivers
2. Connect (auto-detects)
3. Find camera index: `CAMERA_URL = 1`
4. Run system

---

## ✅ Testing Checklist (iOS)

Before going mobile:

- [ ] iPhone camera app installed and working
- [ ] PC can see video stream (test in browser or with app)
- [ ] `client_orchestrator.py` has correct camera URL/index
- [ ] Video appears when running client
- [ ] iPhone is charged or connected to power bank
- [ ] iPhone screen stays on during operation
- [ ] Bluetooth headset connected to PC
- [ ] Both devices on same WiFi network
- [ ] iPhone mounted securely at chest level
- [ ] Guided Access enabled (optional but recommended)

---

## 🆚 iOS vs Android

| Feature | iOS | Android |
|---------|-----|---------|
| **Free IP stream** | WebCamera | IP Webcam ✅ Better |
| **Setup complexity** | Medium | Easy ✅ |
| **Battery life** | Good | Better ✅ |
| **Stream quality** | Good | Good |
| **Virtual webcam** | EpocCam/iVCam | DroidCam |
| **Stability** | Very good ✅ | Good |

**Recommendation**: If you have both iOS and Android, use Android with IP Webcam (easier setup). But iOS works great too with WebCamera or EpocCam!

---

**Need more help?** Check terminal output for errors or see [PHONE_SETUP.md](PHONE_SETUP.md) for general phone setup tips.
