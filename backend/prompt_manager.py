"""
Prompt Manager - Centralized prompt templates with personality and safety controls
Handles all AI interactions with consistent personality and safety guardrails

═══════════════════════════════════════════════════════════════════════════
                        INTENT → NODE → PROMPT MAPPING
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ USER SAYS                    │ INTENT              │ NODE                │
├─────────────────────────────────────────────────────────────────────────┤
│ "Take me to cafeteria"       │ NAVIGATE_TO_DEST    │ NAVIGATE            │
│ "Guide me to washroom"       │ NAVIGATE_TO_DEST    │ NAVIGATE            │
│ "Continue navigation"        │ (active nav)        │ NAVIGATE            │
├─────────────────────────────────────────────────────────────────────────┤
│ "What's around me?"          │ DESCRIBE_SURR       │ DESCRIBE_SURROUND   │
│ "Describe my surroundings"   │ DESCRIBE_SURR       │ DESCRIBE_SURROUND   │
│ "Where am I?"                │ DESCRIBE_SURR       │ DESCRIBE_SURROUND   │
├─────────────────────────────────────────────────────────────────────────┤
│ "Is it safe to walk?"        │ SAFETY_CHECK        │ SAFETY_CHECK        │
│ "Check for obstacles"        │ SAFETY_CHECK        │ SAFETY_CHECK        │
│ "Can I move forward?"        │ SAFETY_CHECK        │ SAFETY_CHECK        │
├─────────────────────────────────────────────────────────────────────────┤
│ "What's in front of me?"     │ WHAT_IS_AHEAD       │ WHAT_IS_AHEAD       │
│ "What's ahead?"              │ WHAT_IS_AHEAD       │ WHAT_IS_AHEAD       │
│ "Check forward"              │ WHAT_IS_AHEAD       │ WHAT_IS_AHEAD       │
├─────────────────────────────────────────────────────────────────────────┤
│ (Center obstacle detected)   │ AUTO_TRIGGER        │ EMERGENCY_STOP      │
│ (Imminent danger detected)   │ AUTO_TRIGGER        │ EMERGENCY_STOP      │
└─────────────────────────────────────────────────────────────────────────┘

INTENT PRIORITY HIERARCHY (for conflict resolution):
1. EMERGENCY_STOP    → Overrides everything (safety first)
2. SAFETY_CHECK      → Takes precedence during uncertain situations
3. NAVIGATE          → Active during route guidance
4. WHAT_IS_AHEAD     → Focused forward check
5. DESCRIBE_SURROUND → General awareness (lowest priority)

AUTOMATIC INTENT ESCALATION:
- If center_obstacle detected → Force EMERGENCY_STOP
- If multiple obstacles (>3) → Escalate to SAFETY_CHECK
- If narrow path detected → Add caution to current intent
- If destination reached → End NAVIGATE mode

"""

from typing import Dict, List, Optional
from enum import Enum

class IntentNode(str, Enum):
    """
    Navigation Intent Nodes - Maps user commands to specific AI behaviors
    
    NAVIGATE: Turn-by-turn directions to reach destination
    DESCRIBE_SURROUNDINGS: 360° environmental awareness (what's around me?)
    SAFETY_CHECK: Path clearance verification (is it safe to move?)
    WHAT_IS_AHEAD: Forward-focused obstacle detection (what's in front?)
    EMERGENCY_STOP: Immediate danger warning (stop now!)
    """
    NAVIGATE = "navigate"
    DESCRIBE_SURROUNDINGS = "describe_surroundings"
    SAFETY_CHECK = "safety_check"
    WHAT_IS_AHEAD = "what_is_ahead"
    EMERGENCY_STOP = "emergency_stop"

class PromptManager:
    """Manages all AI prompts with consistent personality and safety"""
    
    # Master Personality Configuration
    PERSONALITY_CORE = """You are a calm, confident navigation assistant for a visually impaired person.

CORE TRAITS:
- Speak naturally like a trusted friend
- Keep responses under 20 words
- Never use meta-commentary (don't say "I can help you with" or "let me assist")
- Just state what you see and give clear directions
- Prioritize safety - warn about obstacles immediately if they are within 3 meters
- IGNORE any objects that are further than 3 meters away
- Use simple, direct language

TONE:
✓ "Walk forward. Path is clear."
✓ "Stop. Chair directly ahead."
✓ "You're in a hallway. Tables on your right."
✗ "I can help you navigate" (no meta-talk)
✗ "Let me describe the surroundings for you" (just describe)
"""

    # Safety Constraints
    SAFETY_RULES = """
SAFETY FIRST:
- If obstacle ahead → immediate warning
- If path blocked → suggest alternative
- If uncertain → tell user to wait
- Always prioritize caution
"""

    @staticmethod
    def get_prompt(
        intent: IntentNode,
        scene_info: str,
        objects: List[Dict],
        user_context: str,
        destination: str = "destination"
    ) -> str:
        """
        Get dynamic prompt - adapts to situation naturally without rigid templates
        """
        
        # Analyze objects for safety
        safety_analysis = PromptManager._analyze_safety(objects)
        
        # Build dynamic context
        context = f"""{PromptManager.PERSONALITY_CORE}

SITUATION:
{scene_info}

SAFETY: {safety_analysis}

USER NEEDS: {user_context}
"""
        
        # Simple, natural instructions based on what user needs
        if intent == IntentNode.NAVIGATE:
            context += f"\nGuide them one step toward {destination}. Give ONE clear direction based on what you ACTUALLY SEE."
            
        elif intent == IntentNode.DESCRIBE_SURROUNDINGS:
            context += """
Tell them what's ahead and HOW TO NAVIGATE around it.

RULES:
- Identify only objects that are NEAR (< 3 meters) and could be hit.
- IGNORE distant objects entirely.
- If there's an obstacle in the center and it's close: suggest moving to the clearer side.
- Only say "Stop" if the path is completely blocked on all sides within 2 meters.
- Prioritize actionable directions: "Move left", "Go right", "Continue straight".
- Keep it under 10 words.
"""
            
        elif intent == IntentNode.SAFETY_CHECK:
            context += "\nBased on what you SEE, is the path clear? Answer directly: safe or not safe, and state specific obstacles if any."
            
        elif intent == IntentNode.WHAT_IS_AHEAD:
            context += "\nDescribe what you ACTUALLY SEE directly ahead. Don't guess or make assumptions."
            
        elif intent == IntentNode.EMERGENCY_STOP:
            context += "\nDANGER AHEAD. Say STOP and name the obstacle. Be firm but calm."
        
        return context
    
    @staticmethod
    def _analyze_safety(objects: List[Dict]) -> str:
        """Analyze detected objects for safety status"""
        center_obstacles = [o for o in objects if o.get('position') == 'center' and o.get('distance_meters', 2.0) < 3.0]
        left_obstacles = [o for o in objects if o.get('position') == 'left' and o.get('distance_meters', 2.0) < 2.5]
        right_obstacles = [o for o in objects if o.get('position') == 'right' and o.get('distance_meters', 2.0) < 2.5]
        
        relevant_objects = center_obstacles + left_obstacles + right_obstacles
        
        if not relevant_objects:
            return "Path appears clear within 3 meters"
            
        if center_obstacles:
            names = [o['name'] for o in center_obstacles[:2]]
            dist = min([o.get('distance_meters', 2.0) for o in center_obstacles])
            return f"⚠️ DANGER: {', '.join(names)} blocking path at {dist}m"
        elif len(relevant_objects) > 3:
            return f"⚠️ CAUTION: Multiple nearby objects ({len(relevant_objects)} total)"
        elif left_obstacles and right_obstacles:
            return "⚠️ NARROW: Objects on both sides"
        else:
            return "✓ Path appears navigable with caution"
    
    @staticmethod
    def apply_safety_filter(response_text: str, objects: List[Dict]) -> str:
        """
        Apply post-generation safety filter
        Ensures response matches actual safety conditions
        """
        center_obstacles = [o for o in objects if o.get('position') == 'center']
        
        # If center obstacle and response doesn't suggest a direction OR stop, force a stop.
        if center_obstacles:
            lower_text = response_text.lower()
            if 'stop' not in lower_text and 'left' not in lower_text and 'right' not in lower_text:
                obstacle_names = ', '.join([o['name'] for o in center_obstacles[:2]])
                return f"Stop! {obstacle_names} ahead."
        
        # Remove any invented measurements
        dangerous_words = ['meters', 'feet', 'yards', 'inches', 'centimeters']
        for word in dangerous_words:
            if word in response_text.lower():
                # This is a safety violation - replace with safe generic
                return "Move carefully. Let me guide you step by step."
        
        return response_text
    
    @staticmethod
    def get_fallback_response(intent: IntentNode, has_center_obstacle: bool) -> str:
        """Safe fallback if AI fails - no meta-commentary"""
        if has_center_obstacle:
            return "Stop. Obstacle ahead. Wait."
        
        fallbacks = {
            IntentNode.NAVIGATE: "Wait. Processing path.",
            IntentNode.DESCRIBE_SURROUNDINGS: "One moment. Analyzing surroundings.",
            IntentNode.SAFETY_CHECK: "Checking safety. Stand still.",
            IntentNode.WHAT_IS_AHEAD: "Checking ahead. Hold on.",
            IntentNode.EMERGENCY_STOP: "Stop. Wait for guidance."
        }
        
        return fallbacks.get(intent, "Wait for guidance.")


# Convenience function
def get_navigation_prompt(
    intent: str,
    scene_info: str,
    objects: List[Dict],
    user_context: str,
    destination: str = "destination"
) -> str:
    """
    Get prompt for navigation scenario
    
    Args:
        intent: Intent string (e.g., "navigate", "describe_surroundings")
        scene_info: Scene description
        objects: Detected objects list
        user_context: User's current context
        destination: Target destination
        
    Returns:
        Complete prompt string
    """
    try:
        intent_node = IntentNode(intent.lower())
    except ValueError:
        intent_node = IntentNode.NAVIGATE
    
    return PromptManager.get_prompt(
        intent=intent_node,
        scene_info=scene_info,
        objects=objects,
        user_context=user_context,
        destination=destination
    )
