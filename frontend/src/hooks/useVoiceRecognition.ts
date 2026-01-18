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
  const recognitionRef = useRef<InstanceType<
    NonNullable<typeof window.SpeechRecognition>
  > | null>(null);
  const isProcessingRef = useRef(false);
  const commandsRef = useRef(commands);
  const onCommandDetectedRef = useRef(onCommandDetected);

  // Keep refs updated to avoid stale closures
  useEffect(() => {
    commandsRef.current = commands;
  }, [commands]);

  useEffect(() => {
    onCommandDetectedRef.current = onCommandDetected;
  }, [onCommandDetected]);

  const startListening = useCallback(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setIsSupported(false);
      console.info("Speech recognition not available - UI remains fully functional");
      return;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore stop errors
      }
    }

    try {
      const recognition = new SpeechRecognitionAPI();

      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        if (isProcessingRef.current) return;

        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript
          .toLowerCase()
          .trim();

        for (const command of commandsRef.current) {
          for (const phrase of command.phrases) {
            if (transcript.includes(phrase.toLowerCase())) {
              isProcessingRef.current = true;
              onCommandDetectedRef.current?.(phrase);

              recognition.stop();

              setTimeout(() => {
                command.action();
                isProcessingRef.current = false;
              }, 1500);

              return;
            }
          }
        }
      };

      recognition.onerror = (event) => {
        // Graceful degradation - log but don't break UI
        if (event.error !== "aborted" && event.error !== "no-speech") {
          console.info("Voice recognition paused:", event.error);
          setIsListening(false);
        }
      };

      recognition.onend = () => {
        if (!isProcessingRef.current && enabled) {
          // Auto-restart without toggling isListening to prevent flicker
          setTimeout(() => {
            if (!isProcessingRef.current) {
              startListening();
            }
          }, 100);
        } else {
          setIsListening(false);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (error) {
      // Fail silently - UI works without voice
      console.info("Voice recognition unavailable");
      setIsSupported(false);
    }
  }, [enabled]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore stop errors
      }
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  useEffect(() => {
    if (enabled) {
      // Delay to allow initial voice announcement to complete
      const timer = setTimeout(() => {
        startListening();
      }, 3000);
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
