import { useEffect, useRef, useCallback, useState } from "react";

interface VoiceCommand {
  phrases: string[];
  action: () => void;
}

interface UseVoiceRecognitionOptions {
  commands: VoiceCommand[];
  onCommandDetected?: (phrase: string) => void;
  enabled?: boolean;
}

export function useVoiceRecognition({
  commands,
  onCommandDetected,
  enabled = true,
}: UseVoiceRecognitionOptions) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<any>(null);
  const isStartedRef = useRef(false);
  const isProcessingRef = useRef(false);
  const lastStartTimeRef = useRef(0);

  const commandsRef = useRef(commands);
  const onCommandDetectedRef = useRef(onCommandDetected);

  // Keep refs updated to avoid stale closures
  useEffect(() => {
    commandsRef.current = commands;
  }, [commands]);

  useEffect(() => {
    onCommandDetectedRef.current = onCommandDetected;
  }, [onCommandDetected]);

  const stopListening = useCallback(() => {
    console.log("Stopping voice recognition...");
    if (recognitionRef.current) {
      try {
        // Remove listeners to prevent "ended" from triggering a restart during manual stop
        recognitionRef.current.onstart = null;
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;
        recognitionRef.current.stop();
      } catch (e) {
        console.warn("Error stopping recognition:", e);
      }
      recognitionRef.current = null;
    }
    isStartedRef.current = false;
    setIsListening(false);
  }, []);

  const startListening = useCallback(() => {
    const SpeechRecognitionAPI =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setIsSupported(false);
      return;
    }

    if (!enabled || isProcessingRef.current || isStartedRef.current) {
      console.log("Speech start bypassed:", { enabled, isProcessing: isProcessingRef.current, isStarted: isStartedRef.current });
      return;
    }

    // Throttle starts
    const now = Date.now();
    if (now - lastStartTimeRef.current < 1000) {
      console.log("Speech start throttled");
      return;
    }
    lastStartTimeRef.current = now;

    try {
      console.log("Initializing new SpeechRecognition instance...");
      const recognition = new SpeechRecognitionAPI();
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        console.log("Speech recognition started successfully");
        isStartedRef.current = true;
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        if (isProcessingRef.current) return;

        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript
          .toLowerCase()
          .trim();

        console.log("Speech transcript received:", transcript);

        let matched = false;
        for (const command of commandsRef.current) {
          for (const phrase of command.phrases) {
            if (transcript.includes(phrase.toLowerCase())) {
              matched = true;
              isProcessingRef.current = true;
              console.log("Command matched:", phrase);
              onCommandDetectedRef.current?.(phrase);

              stopListening();

              setTimeout(() => {
                command.action();
                isProcessingRef.current = false;
                startListening();
              }, 1500);

              return;
            }
          }
        }

        // If no specific phrase matched, and we are enabled, forward the whole transcript
        if (!matched && onCommandDetectedRef.current) {
          console.log("No specific phrase matched, forwarding full transcript");
          isProcessingRef.current = true;
          onCommandDetectedRef.current(transcript);

          stopListening();

          setTimeout(() => {
            isProcessingRef.current = false;
            startListening();
          }, 2000);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
          setIsSupported(false);
        }
        // If aborted, we'll let onend handle the state Reset
      };

      recognition.onend = () => {
        console.log("Speech recognition instance ended");
        isStartedRef.current = false;
        setIsListening(false);

        // Auto-restart if still enabled and not processing
        if (enabled && !isProcessingRef.current) {
          console.log("Auto-restarting speech recognition...");
          setTimeout(startListening, 300);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (error) {
      console.error("Critical speech recognition failure:", error);
      setIsSupported(false);
    }
  }, [enabled, stopListening]);

  useEffect(() => {
    if (enabled) {
      const timer = setTimeout(() => {
        startListening();
      }, 1000);
      return () => {
        clearTimeout(timer);
        stopListening();
      };
    } else {
      stopListening();
    }
  }, [enabled, startListening, stopListening]);

  return { isListening, isSupported, startListening, stopListening };
}
