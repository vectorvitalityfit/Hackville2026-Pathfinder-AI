import { useState, useEffect, useRef, useCallback } from "react";

interface UseAudioAnalyzerOptions {
  enabled?: boolean;
  smoothingTimeConstant?: number;
  fftSize?: number;
  silenceThreshold?: number;
}

interface UseAudioAnalyzerReturn {
  isListening: boolean;
  isSpeaking: boolean;
  audioLevel: number;
  frequencyData: number[];
  error: string | null;
  startListening: () => Promise<boolean>;
  stopListening: () => void;
}

export const useAudioAnalyzer = ({
  enabled = false,
  smoothingTimeConstant = 0.8,
  fftSize = 64,
  silenceThreshold = 0.05,
}: UseAudioAnalyzerOptions = {}): UseAudioAnalyzerReturn => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [frequencyData, setFrequencyData] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const silenceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const cleanup = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }

    analyzerRef.current = null;
    setIsListening(false);
    setIsSpeaking(false);
    setAudioLevel(0);
    setFrequencyData([]);
  }, []);

  const analyzeAudio = useCallback(() => {
    if (!analyzerRef.current) return;

    const analyzer = analyzerRef.current;
    const dataArray = new Uint8Array(analyzer.frequencyBinCount);
    analyzer.getByteFrequencyData(dataArray);

    // Calculate average amplitude
    const sum = dataArray.reduce((acc, val) => acc + val, 0);
    const average = sum / dataArray.length / 255;

    setAudioLevel(average);

    // Normalize frequency data for visualization (use first 8 bands)
    const bandCount = 8;
    const bandsPerGroup = Math.floor(dataArray.length / bandCount);
    const bands: number[] = [];

    for (let i = 0; i < bandCount; i++) {
      let bandSum = 0;
      for (let j = 0; j < bandsPerGroup; j++) {
        bandSum += dataArray[i * bandsPerGroup + j];
      }
      bands.push((bandSum / bandsPerGroup / 255) * average * 3); // Amplify based on overall level
    }

    setFrequencyData(bands);

    // Determine if speaking based on threshold
    if (average > silenceThreshold) {
      setIsSpeaking(true);

      // Clear existing silence timeout
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }

      // Set a timeout to detect when speaking stops
      silenceTimeoutRef.current = setTimeout(() => {
        setIsSpeaking(false);
      }, 200);
    }

    animationFrameRef.current = requestAnimationFrame(analyzeAudio);
  }, [silenceThreshold]);

  const startListening = useCallback(async (): Promise<boolean> => {
    try {
      setError(null);

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      streamRef.current = stream;

      // Create audio context and analyzer
      const audioContext = new (window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      audioContextRef.current = audioContext;

      const analyzer = audioContext.createAnalyser();
      analyzer.smoothingTimeConstant = smoothingTimeConstant;
      analyzer.fftSize = fftSize;
      analyzerRef.current = analyzer;

      // Connect microphone to analyzer
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyzer);

      setIsListening(true);

      // Start analyzing
      analyzeAudio();

      return true;
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.name === "NotAllowedError"
            ? "Microphone access denied"
            : err.message
          : "Failed to access microphone";

      setError(errorMessage);
      cleanup();
      return false;
    }
  }, [smoothingTimeConstant, fftSize, analyzeAudio, cleanup]);

  const stopListening = useCallback(() => {
    cleanup();
  }, [cleanup]);

  // Auto-start/stop based on enabled prop
  useEffect(() => {
    if (enabled) {
      startListening();
    } else {
      stopListening();
    }

    return () => {
      cleanup();
    };
  }, [enabled, startListening, stopListening, cleanup]);

  return {
    isListening,
    isSpeaking,
    audioLevel,
    frequencyData,
    error,
    startListening,
    stopListening,
  };
};
