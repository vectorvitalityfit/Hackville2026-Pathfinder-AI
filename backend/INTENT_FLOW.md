# Intent & Node Mapping - Voice Navigation System

## 🎯 Intent Flow Architecture

```
┌──────────────────┐
│  User Voice      │
│  Command         │
└────────┬─────────┘
         │
         v
┌──────────────────────────────────┐
│  Speech-to-Text (Google Cloud)   │
│  "Take me to the cafeteria"      │
└────────┬─────────────────────────┘
         │
         v
┌──────────────────────────────────┐
│  Intent Classification (Gemini)  │
│  Returns: NAVIGATE_TO_DESTINATION │
│  Destination: cafeteria           │
└────────┬─────────────────────────┘
         │
         v
┌──────────────────────────────────┐
│  Intent Node Router              │
│  Maps to: NAVIGATE               │
└────────┬─────────────────────────┘
         │
         ├──────────────────────────────────┐
         │                                  │
         v                                  v
┌────────────────┐              ┌──────────────────────┐
│ Vision API     │              │ Prompt Manager       │
│ Object Det.    │───context───>│ Get NAVIGATE prompt  │
└────────────────┘              └──────────┬───────────┘
                                           │
                                           v
                                ┌────────────────────────┐
                                │  Gemini 2.0 Flash      │
                                │  Generate Response     │
                                └──────────┬─────────────┘
                                           │
                                           v
                                ┌────────────────────────┐
                                │  Safety Filter         │
                                │  Validate Response     │
                                └──────────┬─────────────┘
                                           │
                                           v
                                ┌────────────────────────┐
                                │  ElevenLabs TTS        │
                                │  "Turn left..."        │
                                └────────────────────────┘
```

---

## 📋 Complete Intent Mapping Table

| User Command Examples | STT Output | Gemini Intent | Intent Node | Prompt Focus | Example Response |
|----------------------|------------|---------------|-------------|--------------|------------------|
| "Take me to cafeteria"<br>"Guide me to washroom"<br>"Navigate to [place]" | Text string | `NAVIGATE_TO_DESTINATION` | `NAVIGATE` | Turn-by-turn directions | "Turn left. Walk forward. Door ahead." |
| "What's around me?"<br>"Describe surroundings"<br>"Where am I?" | Text string | `DESCRIBE_SURROUNDINGS` | `DESCRIBE_SURROUNDINGS` | 360° environment scan | "Hallway. Tables on right. Wall on left." |
| "Is it safe?"<br>"Check for obstacles"<br>"Can I move forward?" | Text string | `SAFETY_CHECK` | `SAFETY_CHECK` | Path clearance check | "Path is clear. Safe to walk forward." |
| "What's ahead?"<br>"What's in front?"<br>"Check forward" | Text string | `WHAT_IS_AHEAD` | `WHAT_IS_AHEAD` | Forward-only view | "Chair ahead on right. Path on left clear." |
| *(Auto-triggered)* | N/A | *(System)* | `EMERGENCY_STOP` | Immediate stop | "Stop! Chair directly ahead." |

---

## 🔀 Intent Node Details

### 1. **NAVIGATE** Node
**Trigger**: User requests navigation to destination  
**Purpose**: Provide step-by-step walking instructions  
**Response Style**: One direction per message (left/right/straight/stop)  
**Word Limit**: 20 words max  
**Example Prompts**:
- User in hallway → "Continue straight. Keep to the center."
- Obstacle detected → "Stop. Chair on right. Move left."
- Near destination → "Almost there. Door ahead on right."

**Prompt Template**:
```
You are guiding user to {destination}.
Current scene: {scene_info}
Objects: {objects_list}
Safety: {safety_status}

Give ONE walking instruction:
- Direction (left/right/straight/stop)
- Brief obstacle mention if relevant
- Short encouragement

Max 20 words. Be confident and calm.
```

---

### 2. **DESCRIBE_SURROUNDINGS** Node
**Trigger**: User asks "what's around me?"  
**Purpose**: Paint mental picture of environment  
**Response Style**: Space type + 2-4 key objects with positions  
**Word Limit**: 20 words max  
**Example Prompts**:
- Open room → "Open room. Chairs scattered. Window ahead. Feels spacious."
- Hallway → "Narrow hallway. Boxes stacked on sides. Path ahead clear."
- Crowded area → "Busy area. Tables on right. People moving. Stay alert."

**Prompt Template**:
```
Describe the user's surroundings.
Scene: {scene_info}
Objects: {objects_list}

Format:
1. Space type (hallway/room/area)
2. 2-4 key objects with positions
3. Spatial feel (narrow/open/crowded)

Max 20 words. Focus on navigation-relevant items.
```

---

### 3. **SAFETY_CHECK** Node
**Trigger**: User asks "is it safe?"  
**Purpose**: Verify path clearance for movement  
**Response Style**: Clear/Narrow/Blocked + reason  
**Word Limit**: 15 words max  
**Example Prompts**:
- Path clear → "Path is clear. Safe to walk forward."
- Obstacle present → "Not safe. Chair in your path. Wait."
- Narrow path → "Narrow path. Wall left, desk right. Move carefully."

**Safety Criteria**:
- 🟢 **CLEAR**: No obstacles in central path
- 🟡 **NARROW**: Objects on sides, path exists
- 🔴 **BLOCKED**: Obstacle in direct path

**Prompt Template**:
```
Check if it's safe for user to move forward.
Objects: {objects_list}
Safety analysis: {safety_status}

Respond:
- "Path is clear" OR "Not safe" OR "Narrow path"
- Name obstacle if blocked
- Max 15 words
```

---

### 4. **WHAT_IS_AHEAD** Node
**Trigger**: User asks "what's in front?"  
**Purpose**: Forward-focused obstacle detection  
**Response Style**: Forward view only (ignore sides/behind)  
**Word Limit**: 15 words max  
**Example Prompts**:
- Clear ahead → "Clear path ahead. No obstacles."
- Object ahead → "Door ahead, about ten steps."
- Immediate danger → "Wall directly in front. Stop."

**Distance Language**:
- "Right ahead" = 1-2 steps
- "A few steps" = 3-5 steps
- "Ahead" = 5-10 steps
- "Far ahead" = 10+ steps

**Prompt Template**:
```
Describe what's DIRECTLY in front of user.
Forward view only (0-180°).
Objects: {objects_list}

Focus on:
- Immediate obstacle or clear path
- Distance context
- Movement advice (safe/stop/path clear)

Max 15 words. Forward view ONLY.
```

---

### 5. **EMERGENCY_STOP** Node
**Trigger**: System detects center obstacle (auto)  
**Purpose**: Immediate danger warning  
**Response Style**: "Stop!" + danger name  
**Word Limit**: 5-10 words  
**Example Prompts**:
- "Stop! Chair directly ahead."
- "Halt! Wall in front of you."
- "Stop now! Obstacle blocking path."

**Auto-Trigger Conditions**:
- Object position = "center"
- Object confidence > 0.6
- User is in motion (NAVIGATING mode)

**Prompt Template**:
```
⚠️ EMERGENCY STOP REQUIRED ⚠️

Obstacle detected in direct path:
{obstacle_name} at center position

Issue immediate stop command:
- First word: "Stop" or "Halt"
- Name the danger
- 5-10 words ONLY
- Firm but calm tone
```

---

## 🔄 Intent Priority & Conflict Resolution

When multiple intents could apply, use this hierarchy:

```
1. EMERGENCY_STOP     ← Overrides everything (safety first)
   └─ Auto-triggered by center obstacles
   
2. SAFETY_CHECK       ← Takes precedence in uncertain situations
   └─ User explicitly asks for safety verification
   
3. NAVIGATE           ← Active during route guidance
   └─ User has started navigation to destination
   
4. WHAT_IS_AHEAD      ← Focused forward check
   └─ User wants specific forward view
   
5. DESCRIBE_SURROUND  ← General awareness (lowest priority)
   └─ User wants broad environmental info
```

**Example Conflict**:
- User says: "Describe my surroundings"
- System detects: Center obstacle
- **Resolution**: Force EMERGENCY_STOP (safety overrides user intent)
- Response: "Stop! Chair directly ahead." *(then can describe after)*

---

## ⚙️ Automatic Intent Escalation Rules

The system can automatically change intents based on detected conditions:

| Condition | Auto-Escalation | Reason |
|-----------|----------------|--------|
| Center obstacle detected | → `EMERGENCY_STOP` | Imminent collision risk |
| 3+ obstacles detected | → `SAFETY_CHECK` | Complex environment |
| User in NAVIGATE mode + narrow path | Add "caution" flag | Maintain awareness |
| Destination reached | End NAVIGATE mode | Goal accomplished |
| Vision API fails | Use Gemini fallback | Maintain functionality |

---

## 🧠 Prompt Manager Safety Filters

Every AI response goes through post-generation filters:

### 1. **Safety Filter** (`apply_safety_filter()`)
```python
# Checks:
- If center_obstacle exists + response doesn't say "stop"
  → Force: "Stop! {obstacle} directly ahead."
  
- If response contains measurements (meters/feet)
  → Replace: "Move carefully. Let me guide you."
```

### 2. **Fallback Responses** (`get_fallback_response()`)
```python
# If Gemini fails:
NAVIGATE        → "Please wait. I'm processing the path."
DESCRIBE        → "I'm analyzing your surroundings. One moment."
SAFETY_CHECK    → "Checking safety. Please stand still."
WHAT_IS_AHEAD   → "Checking what's ahead. Hold on."
EMERGENCY_STOP  → "Stop immediately. Wait for guidance."
```

### 3. **Format Cleanup**
```python
# Remove:
- Asterisks: *text* → text
- Hash symbols: # heading → heading
- Multiple spaces → single space
```

---

## 🎨 Personality Consistency

All prompts share the same personality core:

```
PERSONALITY:
✓ Calm, confident, and warm
✓ Patient friend who guides without rushing
✓ Professional but never robotic
✓ Brief but reassuring

TONE EXAMPLES:
✓ "Walk forward. Path is clear."
✓ "Stop! Chair directly ahead."
✓ "Turn left. Take your time."

FORBIDDEN:
✗ "Proceed 3.7 meters forward" (too technical)
✗ "You should probably maybe go left" (not confident)
✗ Long explanations (stay concise)
```

---

## 📊 Intent Usage Statistics (Typical Session)

```
Session: User navigates to cafeteria (5 minutes)

NAVIGATE:           ████████████████░░ 80% (16 calls)
SAFETY_CHECK:       ██░░░░░░░░░░░░░░░░ 10% (2 calls)
WHAT_IS_AHEAD:      █░░░░░░░░░░░░░░░░░  5% (1 call)
DESCRIBE_SURROUND:  █░░░░░░░░░░░░░░░░░  5% (1 call)
EMERGENCY_STOP:     ░░░░░░░░░░░░░░░░░░  0% (0 calls)

Most common: NAVIGATE (active guidance)
Least common: EMERGENCY_STOP (safety systems working)
```

---

## 🔧 Developer Guide: Adding New Intent

To add a new intent node:

1. **Add to Enum** (`prompt_manager.py`):
```python
class IntentNode(str, Enum):
    YOUR_NEW_INTENT = "your_new_intent"
```

2. **Create Prompt Template** (`PromptManager.get_prompt()`):
```python
elif intent == IntentNode.YOUR_NEW_INTENT:
    return base_context + """
    YOUR DETAILED PROMPT HERE
    """
```

3. **Add Fallback** (`get_fallback_response()`):
```python
fallbacks = {
    IntentNode.YOUR_NEW_INTENT: "Safe fallback message here."
}
```

4. **Map in Command Interpreter** (`routes/command.py`):
```python
# Add to intent classification prompt
```

5. **Update Client** (`client_orchestrator.py`):
```python
elif intent == "YOUR_NEW_INTENT":
    state.active_mode = "YOUR_MODE"
    # Handle the intent
```

---

## 🧪 Testing Intent Flows

Test each intent with sample scenarios:

```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Start client
python client_orchestrator.py

# Test commands:
- "Take me to the cafeteria"     → NAVIGATE
- "What's around me?"            → DESCRIBE_SURROUNDINGS
- "Is it safe to walk?"          → SAFETY_CHECK
- "What's ahead?"                → WHAT_IS_AHEAD
- (Place object in camera)       → EMERGENCY_STOP (auto)
```

---

## 📚 Related Files

- **Prompt Templates**: `prompt_manager.py`
- **Intent Router**: `routes/brain.py`
- **Intent Classification**: `routes/command.py`
- **Client Handler**: `client_orchestrator.py`
- **Safety Middleware**: `app/main.py`

---

**Last Updated**: January 18, 2026  
**Version**: 0.2.0  
**Status**: ✅ Production Ready
