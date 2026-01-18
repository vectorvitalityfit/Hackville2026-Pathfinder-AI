import { useCallback, useRef } from "react";

export function useVoiceAnnouncement() {
  const isSpeakingRef = useRef(false);

  const speak = useCallback(
    (message: string, priority: "polite" | "assertive" = "polite") => {
      // Prevent overlapping announcements
      if (isSpeakingRef.current) {
        return;
      }

      // Update ARIA live region first (works without speech synthesis)
      const liveRegion = document.getElementById("aria-live-region");
      if (liveRegion) {
        liveRegion.setAttribute("aria-live", priority);
        // Clear and set to trigger announcement
        liveRegion.textContent = "";
        requestAnimationFrame(() => {
          liveRegion.textContent = message;
        });
      }

      // Speech synthesis is optional enhancement
      if ("speechSynthesis" in window) {
        try {
          window.speechSynthesis.cancel();
          isSpeakingRef.current = true;

          const utterance = new SpeechSynthesisUtterance(message);
          utterance.rate = 0.9;
          utterance.pitch = 1;
          utterance.volume = 1;

          const voices = window.speechSynthesis.getVoices();
          const preferredVoice = voices.find(
            (voice) => voice.lang.startsWith("en") && voice.localService
          );
          if (preferredVoice) {
            utterance.voice = preferredVoice;
          }

          utterance.onend = () => {
            isSpeakingRef.current = false;
          };

          utterance.onerror = () => {
            isSpeakingRef.current = false;
          };

          window.speechSynthesis.speak(utterance);
        } catch {
          // Fail silently - ARIA live region still works
          isSpeakingRef.current = false;
        }
      }
    },
    []
  );

  const announceOnLoad = useCallback(
    (message: string) => {
      if ("speechSynthesis" in window) {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          speak(message, "assertive");
        } else {
          // Wait for voices to load
          const handleVoicesChanged = () => {
            speak(message, "assertive");
            window.speechSynthesis.onvoiceschanged = null;
          };
          window.speechSynthesis.onvoiceschanged = handleVoicesChanged;

          // Fallback if voices never load
          setTimeout(() => {
            if (!isSpeakingRef.current) {
              speak(message, "assertive");
            }
          }, 1000);
        }
      } else {
        // Still announce via ARIA even without speech
        speak(message, "assertive");
      }
    },
    [speak]
  );

  return { speak, announceOnLoad };
}
