import { useState, useRef, useCallback, useEffect } from "react";

interface UseMediaDevicesOptions {
  onError?: (error: string) => void;
}

export function useMediaDevices({ onError }: UseMediaDevicesOptions = {}) {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isMicActive, setIsMicActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [micError, setMicError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const cameraStreamRef = useRef<MediaStream | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);

  const startCamera = useCallback(async () => {
    try {
      setCameraError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      cameraStreamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsCameraActive(true);
      return true;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Camera access denied";
      setCameraError(message);
      onError?.(`Camera error: ${message}`);
      setIsCameraActive(false);
      return false;
    }
  }, [onError]);

  const stopCamera = useCallback(() => {
    if (cameraStreamRef.current) {
      cameraStreamRef.current.getTracks().forEach((track) => track.stop());
      cameraStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setCameraError(null);
  }, []);

  const startMicrophone = useCallback(async () => {
    try {
      setMicError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      micStreamRef.current = stream;
      setIsMicActive(true);
      return true;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Microphone access denied";
      setMicError(message);
      onError?.(`Microphone error: ${message}`);
      setIsMicActive(false);
      return false;
    }
  }, [onError]);

  const stopMicrophone = useCallback(() => {
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach((track) => track.stop());
      micStreamRef.current = null;
    }
    setIsMicActive(false);
    setMicError(null);
  }, []);

  const toggleCamera = useCallback(async () => {
    if (isCameraActive) {
      stopCamera();
      return false;
    } else {
      return await startCamera();
    }
  }, [isCameraActive, startCamera, stopCamera]);

  const toggleMicrophone = useCallback(async () => {
    if (isMicActive) {
      stopMicrophone();
      return false;
    } else {
      return await startMicrophone();
    }
  }, [isMicActive, startMicrophone, stopMicrophone]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
      stopMicrophone();
    };
  }, [stopCamera, stopMicrophone]);

  return {
    videoRef,
    isCameraActive,
    isMicActive,
    cameraError,
    micError,
    startCamera,
    stopCamera,
    startMicrophone,
    stopMicrophone,
    toggleCamera,
    toggleMicrophone,
  };
}
