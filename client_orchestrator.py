import cv2
import requests
import base64
import json
import threading
import time
import os
import sys
import pyaudio
import wave
from playsound import playsound

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# Camera Configuration
# Option 1: Use laptop/PC webcam
# CAMERA_URL = 0

# Option 2: Use phone camera via IP Webcam app
# Install "IP Webcam" from Play Store, start server, and use the URL shown
# Format: "http://192.168.1.XXX:8080/video"
CAMERA_URL = 0  # Change this to your phone's IP Webcam URL

TEMP_AUDIO_FILE = "response.mp3"
RECORD_FILE = "command.wav"

# Audio Recording Settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 3  # Record for 3 seconds when triggered

# --- State ---
class State:
    active_mode = "IDLE" # IDLE, NAVIGATING
    destination = None
    running = True

state = State()

def play_audio(audio_base64):
    """Decode base64 audio and play it"""
    try:
        with open(TEMP_AUDIO_FILE, "wb") as f:
            f.write(base64.b64decode(audio_base64))
        
        # Play asynchronously or synchronously depending on need
        # Using sync for now to ensure message completes before next
        # If file exists, remove it first to avoid locks? playsound 1.2.2 usually handles overwrites okay-ish on exit
        print("🔊 Playing audio...")
        playsound(TEMP_AUDIO_FILE)
        
        # Cleanup
        if os.path.exists(TEMP_AUDIO_FILE):
             os.remove(TEMP_AUDIO_FILE)
    except Exception as e:
        print(f"Audio Error: {e}")

def get_speech_for_text(text):
    """Convert text to speech via backend"""
    try:
        print(f"DEBUG: Requesting TTS for: '{text[:50]}...'")
        r = requests.post(f"{BACKEND_URL}/speech/speak", json={"text": text})
        if r.status_code == 200:
            audio_b64 = r.json().get("audio_base64")
            print(f"DEBUG: TTS successful, audio size: {len(audio_b64) if audio_b64 else 0} chars")
            return audio_b64
        else:
            print(f"DEBUG: TTS failed with status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"TTS Error: {e}")
    return None

def record_audio_command():
    """Record audio from microphone and save to file"""
    print("\n🎤 Recording... (speak now)")
    
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    frames = []
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("✅ Recording complete")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save as WAV file
    wf = wave.open(RECORD_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return RECORD_FILE

def process_voice_command():
    """Record voice and send to backend for interpretation"""
    try:
        # Record audio
        audio_file = record_audio_command()
        
        print("🔄 Processing voice command...")
        
        # Send to /command/interpret-voice endpoint
        with open(audio_file, 'rb') as f:
            files = {'file': (audio_file, f, 'audio/wav')}
            r = requests.post(f"{BACKEND_URL}/command/interpret-voice", files=files)
        
        if r.status_code != 200:
            print(f"Voice Command Error: {r.text}")
            return
        
        data = r.json()
        transcription = data.get("transcription", "")
        intent = data["intent"]
        dest = data.get("destination")
        
        print(f"📝 You said: '{transcription}'")
        print(f"Intent: {intent}, Dest: {dest}")
        
        # Process intent (same logic as text command)
        handle_intent(intent, dest, transcription)
        
    except Exception as e:
        print(f"Voice processing error: {e}")
        import traceback
        traceback.print_exc()

def handle_intent(intent, dest, original_text=""):
    """Handle the interpreted intent"""
    if intent == "NAVIGATE_TO_DESTINATION":
        if dest:
            # Start navigation session
            r_nav = requests.post(f"{BACKEND_URL}/navigation/start", json={"destination": dest})
            if r_nav.status_code == 200:
                state.active_mode = "NAVIGATING"
                state.destination = dest
                print(f"✅ Navigation started to {dest}")
                
                # Announce start
                audio = get_speech_for_text(f"Going to {dest}. Follow me.")
                if audio: play_audio(audio)
            else:
                print("Failed to start navigation backend session")
                audio = get_speech_for_text("Can't reach that destination.")
                if audio: play_audio(audio)
        else:
            print("Destination not recognized")
            audio = get_speech_for_text("Where do you want to go? Cafeteria or washroom?")
            if audio: play_audio(audio)

    elif intent == "DESCRIBE_SURROUNDINGS":
        state.active_mode = "DESCRIBE_ONCE"
        print("👁️ Analyzing surroundings...")
        # No prep audio - just analyze and respond directly

    elif intent == "WHAT_IS_AHEAD":
        state.active_mode = "WHAT_IS_AHEAD"
        print("👁️ Checking what's ahead...")
        # No prep audio - just analyze and respond directly
        
    elif intent == "SAFETY_CHECK":
        state.active_mode = "SAFETY_CHECK"
        print("🛡️ Checking safety...")
        # No prep audio - just analyze and respond directly

    else:
        print("Unknown command")
        audio = get_speech_for_text("Didn't catch that. Try again.")
        if audio: play_audio(audio)

def command_listener():
    """Thread to listen for voice trigger (press Enter to speak)"""
    print("🎤 Voice Command System Active")
    print("Press ENTER to record a voice command (speak for 3 seconds)")
    print("Type 'quit' or 'exit' to stop")
    
    while state.running:
        try:
            user_input = input()
            if user_input.lower() in ["quit", "exit"]:
                state.running = False
                break
            
            # Any other input (including Enter) triggers voice recording
            process_voice_command()
            
        except EOFError:
            break
        except KeyboardInterrupt:
            state.running = False
            break

def capture_and_encode_frame(cap):
    ret, frame = cap.read()
    if not ret:
        return None
    
    # Resize to speed up transfer (640x480 is plenty)
    frame = cv2.resize(frame, (640, 480))
    
    # Encode
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes() #, frame (if we wanted to show it)

def main_loop():
    # Setup Camera
    print(f"📷 connecting to camera: {CAMERA_URL} ...")
    cap = cv2.VideoCapture(CAMERA_URL)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Startup greeting - natural, no meta-commentary
    greeting = "Hello. I'm here to guide you. Press Enter to speak anytime."
    print(f"\n🤖 {greeting}\n")
    audio = get_speech_for_text(greeting)
    if audio:
        play_audio(audio)
    
    # Start command thread
    cmd_thread = threading.Thread(target=command_listener, daemon=True)
    cmd_thread.start()

    print("\n🚀 System Ready!")
    print("Modes: IDLE, NAVIGATING")
    
    last_process_time = 0
    PROCESS_INTERVAL = 2.0 # Process every 2 seconds to avoid spamming APIs

    while state.running:
        current_time = time.time()
        
        # Capture frame always (to clear buffer)
        img_bytes = capture_and_encode_frame(cap)
        if img_bytes is None:
            print("Failed to grab frame")
            time.sleep(1)
            continue
            
        # Logic Loop
        if current_time - last_process_time > PROCESS_INTERVAL:
            
            if state.active_mode == "NAVIGATING":
                # --- NAVIGATION MODE ---
                print("\n[NAV] Processing frame...")
                try:
                    files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}
                    r = requests.post(f"{BACKEND_URL}/navigation/guide", files=files)
                    
                    if r.status_code == 200:
                        data = r.json()
                        step = data["current_step"]
                        speech = data["speech_text"]
                        obstacles = data["obstacles"]
                        
                        print(f"Step: {step}")
                        if obstacles:
                             print(f"Obstacles: {[o['name'] for o in obstacles]}")
                        
                        # Play Audio
                        if speech:
                            print(f"🗣️ Gemini: {speech}")
                            # Get audio for this text
                            audio_b64 = get_speech_for_text(speech)
                            if audio_b64:
                                play_audio(audio_b64)
                        
                        if step == "STOP":
                            print("⛔ SAFETY STOP TRIGGERED")
                            
                except Exception as e:
                    print(f"Nav Error: {e}")
                
                last_process_time = current_time

            elif state.active_mode in ["DESCRIBE_ONCE", "WHAT_IS_AHEAD", "SAFETY_CHECK"]:
                # --- VISION DESCRIPTION MODE ---
                current_intent = state.active_mode.lower()
                print(f"\n[{state.active_mode}] Analyzing single frame...")
                try:
                    files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}
                    
                    # 1. Vision Analysis
                    r_viz = requests.post(f"{BACKEND_URL}/vision/analyze-frame", files=files)
                    viz_data = r_viz.json()
                    
                    # Build object list for speech
                    objects_detected = viz_data.get("objects", [])
                    scene_desc = viz_data.get("scene_description", "")
                    # Build scene data for brain
                    objects_detected = viz_data.get("objects", [])
                    scene_desc = viz_data.get("scene_description", "")
                    
                    # 2. Brain Description with intent-specific context
                    context_map = {
                        "describe_once": "Describe what's around them.",
                        "what_is_ahead": "What's directly ahead in their path.",
                        "safety_check": "Is it safe to walk forward."
                    }
                    user_context = context_map.get(current_intent, "Describe surroundings.")
                    
                    r_brain = requests.post(f"{BACKEND_URL}/brain/describe", json={
                        "scene_description": scene_desc,
                        "objects": objects_detected,
                        "destination": "current location",
                        "user_context": user_context,
                        "intent": current_intent
                    })
                    
                    if r_brain.status_code != 200:
                        print(f"Brain API Error: {r_brain.status_code} - {r_brain.text}")
                        raise Exception(f"Brain API returned {r_brain.status_code}")
                    
                    brain_data = r_brain.json()
                    speech_text = brain_data["speech_text"]
                    
                    print(f"🗣️ Assistant: {speech_text}")
                    
                    # 3. Speech - use the response directly, no extra prefixes
                    audio_b64 = get_speech_for_text(speech_text)
                    if audio_b64:
                        play_audio(audio_b64)
                    else:
                        print("DEBUG: No audio received from TTS!")
                        
                except Exception as e:
                    print(f"Describe Error: {e}")
                    error_msg = "Sorry, I'm having trouble analyzing the scene right now."
                    audio = get_speech_for_text(error_msg)
                    if audio: play_audio(audio)
                
                state.active_mode = "IDLE" # Reset after one-shot
                last_process_time = current_time

        # Small sleep to yield CPU
        time.sleep(0.1)

    cap.release()
    print("System Shutdown.")

if __name__ == "__main__":
    main_loop()

