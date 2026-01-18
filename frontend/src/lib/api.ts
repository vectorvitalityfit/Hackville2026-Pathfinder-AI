// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin;

export const API_ENDPOINTS = {
  vision: {
    analyzeFrame: `${API_BASE_URL}/vision/analyze-frame`,
  },
  brain: {
    describe: `${API_BASE_URL}/brain/describe`,
  },
  speech: {
    speak: `${API_BASE_URL}/speech/speak`,
  },
  command: {
    interpretVoice: `${API_BASE_URL}/command/interpret-voice`,
  },
  navigation: {
    start: `${API_BASE_URL}/navigation/start`,
    stop: `${API_BASE_URL}/navigation/stop`,
  },
  health: `${API_BASE_URL}/health`,
};

// Helper function to convert video frame to blob
export const captureVideoFrame = async (videoElement: HTMLVideoElement): Promise<Blob> => {
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error('Could not get canvas context');
  }

  ctx.drawImage(videoElement, 0, 0);

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('Failed to capture frame'));
      }
    }, 'image/jpeg', 0.8);
  });
};

// Navigation service for continuous obstacle detection
export class NavigationService {
  private isActive = false;
  private intervalId: number | null = null;
  private videoElement: HTMLVideoElement | null = null;
  private onGuidance: ((text: string) => void) | null = null;
  private lastObstacleState: string | null = null;
  private isProcessing = false;

  constructor(videoElement: HTMLVideoElement, onGuidance: (text: string) => void) {
    this.videoElement = videoElement;
    this.onGuidance = onGuidance;
  }

  start() {
    if (this.isActive) return;

    this.isActive = true;
    this.lastObstacleState = null;

    // Immediate first scan
    this.monitorSurroundings();

    // Then every 2 seconds
    this.intervalId = window.setInterval(() => {
      if (!this.isProcessing) {
        this.monitorSurroundings();
      }
    }, 2000);
  }

  stop() {
    this.isActive = false;

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    this.lastObstacleState = null;
  }

  private async monitorSurroundings() {
    if (!this.isActive || !this.videoElement || this.isProcessing) return;

    this.isProcessing = true;

    try {
      // Capture frame
      const imageBlob = await captureVideoFrame(this.videoElement);

      // Vision analysis
      const visionForm = new FormData();
      visionForm.append('file', imageBlob, 'frame.jpg');

      const visionResp = await fetch(API_ENDPOINTS.vision.analyzeFrame, {
        method: 'POST',
        body: visionForm,
      });

      const visionData = await visionResp.json();

      // Analyze obstacles and provide guidance
      const guidance = await this.analyzeObstaclesAndGuide(visionData);

      if (guidance && this.onGuidance) {
        this.onGuidance(guidance);
      }
    } catch (error) {
      console.error('Monitor error:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  private async analyzeObstaclesAndGuide(visionData: any): Promise<string | null> {
    const objects = visionData.objects || [];

    // Filter for relevant nearby objects only
    const relevantNearObjects = objects.filter((obj: any) => {
      const distance = obj.distance_meters || 2.0;
      const pos = obj.position?.toLowerCase() || '';
      if (pos.includes('center') || pos.includes('middle')) return distance < 3.0;
      return distance < 2.5;
    });

    if (relevantNearObjects.length === 0) {
      if (this.lastObstacleState !== 'clear') {
        this.lastObstacleState = 'clear';
      }
      return null;
    }

    // Categorize by position
    const centerObstacles: any[] = [];
    const leftObstacles: any[] = [];
    const rightObstacles: any[] = [];

    relevantNearObjects.forEach((obj: any) => {
      const pos = obj.position?.toLowerCase() || '';
      if (pos.includes('center') || pos.includes('middle')) {
        centerObstacles.push(obj);
      } else if (pos.includes('left')) {
        leftObstacles.push(obj);
      } else if (pos.includes('right')) {
        rightObstacles.push(obj);
      } else {
        centerObstacles.push(obj);
      }
    });

    // Natural guidance
    let guidance = '';

    if (centerObstacles.length > 0) {
      const obj = centerObstacles[0];
      const name = obj.name || 'obstacle';

      if (leftObstacles.length < rightObstacles.length) {
        guidance = `${name} ahead. Go left.`;
      } else if (rightObstacles.length < leftObstacles.length) {
        guidance = `${name} ahead. Go right.`;
      } else {
        guidance = `${name} ahead. Stop.`;
      }
    }

    // Only speak if obstacles changed (by name, not just count)
    const currentObstacles = centerObstacles.map(o => o.name).sort().join(',');

    if (this.lastObstacleState === currentObstacles) {
      return null; // Same obstacles, don't repeat
    }

    this.lastObstacleState = currentObstacles;

    // Use Gemini to generate natural, helpful guidance
    if (centerObstacles.length > 0) {
      try {
        const brainResp = await fetch(API_ENDPOINTS.brain.describe, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scene_description: `Center: ${centerObstacles.map(o => o.name).join(', ')}. Left: ${leftObstacles.map(o => o.name).join(', ') || 'clear'}. Right: ${rightObstacles.map(o => o.name).join(', ') || 'clear'}.`,
            objects: relevantNearObjects,
            destination: 'walking forward',
            user_context: 'Provide natural navigation guidance in a complete sentence',
            intent: 'DESCRIBE_SURROUNDINGS'
          }),
        });

        const brainData = await brainResp.json();
        return brainData.speech_text || guidance;
      } catch (error) {
        console.error('Gemini guidance error:', error);
        return guidance; // Fallback to simple guidance
      }
    }

    return guidance;
  }
}

// Speech synthesis helper
export const playAudioResponse = async (text: string): Promise<void> => {
  try {
    const response = await fetch(API_ENDPOINTS.speech.speak, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`TTS failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data.audio_base64) {
      throw new Error('No audio data received');
    }

    // Play audio
    const audio = new Audio('data:audio/mpeg;base64,' + data.audio_base64);
    await audio.play();

    // Wait for audio to finish
    return new Promise((resolve) => {
      audio.onended = () => resolve();
    });
  } catch (error) {
    console.error('Speech error:', error);
    throw error;
  }
};

// Voice command processing
export const processVoiceCommand = async (
  audioBlob: Blob,
  videoElement: HTMLVideoElement
): Promise<{ text: string; intent: string; destination?: string }> => {
  try {
    // Capture frame
    const imageBlob = await captureVideoFrame(videoElement);

    // Send voice command
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');

    const cmdResponse = await fetch(API_ENDPOINTS.command.interpretVoice, {
      method: 'POST',
      body: formData,
    });

    const cmdData = await cmdResponse.json();
    const intent = cmdData.intent;
    const destination = cmdData.destination;
    const transcription = cmdData.transcription || '';

    // Process based on intent
    if (intent === 'NAVIGATE_TO_DESTINATION' && destination) {
      // Start navigation
      await fetch(API_ENDPOINTS.navigation.start, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destination }),
      });

      return {
        text: `Navigating to ${destination}. Starting continuous guidance.`,
        intent,
        destination,
      };
    } else {
      // Get scene description
      const visionForm = new FormData();
      visionForm.append('file', imageBlob, 'frame.jpg');

      const visionResp = await fetch(API_ENDPOINTS.vision.analyzeFrame, {
        method: 'POST',
        body: visionForm,
      });

      const visionData = await visionResp.json();

      // Brain processing
      const brainResp = await fetch(API_ENDPOINTS.brain.describe, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_description: visionData.scene_description || '',
          objects: visionData.objects || [],
          destination: 'current location',
          user_context: 'Describe surroundings.',
          intent: intent,
        }),
      });

      const brainData = await brainResp.json();

      return {
        text: brainData.speech_text,
        intent,
      };
    }
  } catch (error) {
    console.error('Voice command error:', error);
    throw error;
  }
};

export const processTextCommand = async (
  text: string,
  videoElement: HTMLVideoElement
): Promise<{ text: string; intent: string; destination?: string }> => {
  try {
    // Interpret text command
    const interpretUrl = API_ENDPOINTS.command.interpretVoice.replace('interpret-voice', 'interpret');

    const cmdResponse = await fetch(interpretUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    const cmdData = await cmdResponse.json();
    const intent = cmdData.intent;
    const destination = cmdData.destination;

    // Process based on intent
    if (intent === 'NAVIGATE_TO_DESTINATION' && destination) {
      // Start navigation
      await fetch(API_ENDPOINTS.navigation.start, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destination }),
      });

      return {
        text: `Navigating to ${destination}. Starting continuous guidance.`,
        intent,
        destination,
      };
    } else {
      // Get scene description
      const imageBlob = await captureVideoFrame(videoElement);
      const visionForm = new FormData();
      visionForm.append('file', imageBlob, 'frame.jpg');

      const visionResp = await fetch(API_ENDPOINTS.vision.analyzeFrame, {
        method: 'POST',
        body: visionForm,
      });

      const visionData = await visionResp.json();

      // Brain processing
      const brainResp = await fetch(API_ENDPOINTS.brain.describe, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_description: visionData.scene_description || '',
          objects: visionData.objects || [],
          destination: 'current location',
          user_context: text,
          intent: intent,
        }),
      });

      const brainData = await brainResp.json();

      return {
        text: brainData.speech_text,
        intent,
      };
    }
  } catch (error) {
    console.error('Text command error:', error);
    throw error;
  }
};
