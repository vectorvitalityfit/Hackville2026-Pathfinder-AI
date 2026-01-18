# Voice Navigation Frontend - Configuration

This frontend is configured to work with the Voice Navigation Backend.

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Start dev server (connects to backend at same origin)
npm run dev
```

### With Backend

```bash
# Terminal 1: Start Backend
cd ..
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend  
npm run dev

# Terminal 3: Expose with ngrok
ngrok http 8000
```

## Features Implemented

### 🦯 Real-Time Obstacle Detection
- Continuous monitoring every 2 seconds
- Directional guidance (left/right/center)
- Smart state tracking (doesn't repeat same warnings)
- Automatic speech synthesis

### 🎤 Voice Commands
Available commands (see backend for full list):
- "Navigate to [destination]" - Start navigation to a place
- "What's around me?" - Describe surroundings
- "What do you see?" - Analyze current view
- "Stop navigation" - Stop continuous guidance

### 📡 API Integration
All backend endpoints are configured:
- `/vision/analyze-frame` - Visual analysis
- `/brain/describe` - Scene understanding
- `/speech/speak` - Text-to-speech
- `/command/interpret-voice` - Voice command processing
- `/navigation/start` - Start navigation
- `/navigation/stop` - Stop navigation

## Configuration

### API URL
Set in `.env` file:
```env
VITE_API_URL=https://your-backend-url.com
```

Leave empty for same-origin (default).

## Usage

1. **Start Assistance** - Activates camera and microphone
2. **Speak Commands** - Say navigation or query commands
3. **Continuous Mode** - Automatically warns about obstacles in real-time

## Mobile Testing

Use ngrok to test on phone:
```bash
# Backend serves both API and frontend
ngrok http 8000
```

Open the ngrok URL on your phone!
