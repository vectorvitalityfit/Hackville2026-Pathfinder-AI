import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere } from "@react-three/drei";
import * as THREE from "three";

interface StatusOrbProps {
  className?: string;
  size?: number;
  isListening?: boolean;
  audioLevel?: number; // 0-1 normalized audio level
}

interface AnimatedSphereProps {
  isListening: boolean;
  audioLevel: number;
  prefersReducedMotion: boolean;
}

function AnimatedSphere({ isListening, audioLevel, prefersReducedMotion }: AnimatedSphereProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Create a gradient shader material so rotation is visible
  const material = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        colorA: { value: new THREE.Color().setHSL(200 / 360, 0.98, 0.7) },
        colorB: { value: new THREE.Color().setHSL(200 / 360, 0.98, 0.35) },
        colorC: { value: new THREE.Color().setHSL(210 / 360, 0.95, 0.55) },
      },
      vertexShader: `
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vPosition = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 colorA;
        uniform vec3 colorB;
        uniform vec3 colorC;
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          // Create a swirl pattern based on position
          float angle = atan(vPosition.x, vPosition.z);
          float pattern = sin(angle * 3.0 + vPosition.y * 2.0) * 0.5 + 0.5;
          
          // Blend colors based on pattern and height
          vec3 color = mix(colorA, colorB, pattern);
          color = mix(color, colorC, smoothstep(-0.5, 0.5, vPosition.y) * 0.5);
          
          // Add lighting based on normal
          float light = dot(vNormal, normalize(vec3(1.0, 1.0, 1.0))) * 0.3 + 0.7;
          
          gl_FragColor = vec4(color * light, 1.0);
        }
      `,
    });
  }, []);

  useFrame(() => {
    if (!meshRef.current || prefersReducedMotion) return;

    // Spin based on audio level: 0.5° to 8° per frame
    const rotationSpeed = isListening 
      ? THREE.MathUtils.degToRad(0.5 + audioLevel * 7.5)
      : THREE.MathUtils.degToRad(0.2);
    
    meshRef.current.rotation.y += rotationSpeed;
  });

  return (
    <Sphere ref={meshRef} args={[1, 64, 64]} material={material} />
  );
}

export function StatusOrb({ 
  className = "", 
  size = 60, 
  isListening = false, 
  audioLevel = 0 
}: StatusOrbProps) {
  // Detect reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' 
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches 
    : false;

  return (
    <div
      className={`flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <Canvas
        camera={{ position: [0, 0, 3], fov: 50 }}
        style={{ 
          width: size, 
          height: size,
          background: 'transparent'
        }}
        gl={{ alpha: true, antialias: true }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={1} color="#ffffff" />

        {/* 3D Sphere with visible gradient pattern */}
        <AnimatedSphere
          isListening={isListening}
          audioLevel={audioLevel}
          prefersReducedMotion={prefersReducedMotion}
        />
      </Canvas>
    </div>
  );
}
