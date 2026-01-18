import { motion, useReducedMotion, Variants } from "framer-motion";

interface LogoProps {
  className?: string;
  size?: number;
  variant?: 'color' | 'monochrome';
  animate?: boolean;
}

export function Logo({ className = "", size = 280, variant = 'color', animate = true }: LogoProps) {
  const prefersReducedMotion = useReducedMotion();
  const shouldAnimate = animate && !prefersReducedMotion;
  
  // Color palette based on design system
  const primaryColor = variant === 'color' ? 'hsl(200, 98%, 50%)' : 'currentColor';
  const secondaryColor = variant === 'color' ? 'hsl(200, 98%, 65%)' : 'currentColor';
  const tertiaryColor = variant === 'color' ? 'hsl(200, 98%, 80%)' : 'currentColor';

  // Animation variants for staggered entrance
  const containerVariants: Variants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94] as const,
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const outerRingVariants: Variants = {
    hidden: { opacity: 0, scale: 0.5 },
    visible: {
      opacity: 0.4,
      scale: 1,
      transition: { duration: 0.6 },
    },
  };

  const middleRingVariants: Variants = {
    hidden: { opacity: 0, scale: 0.5 },
    visible: {
      opacity: 0.6,
      scale: 1,
      transition: { duration: 0.6 },
    },
  };

  const innerRingVariants: Variants = {
    hidden: { opacity: 0, scale: 0.5 },
    visible: {
      opacity: 0.8,
      scale: 1,
      transition: { duration: 0.6 },
    },
  };

  const pathVariants: Variants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: {
      pathLength: 1,
      opacity: 1,
      transition: {
        pathLength: { duration: 0.8 },
        opacity: { duration: 0.3 },
      },
    },
  };

  const beaconVariants: Variants = {
    hidden: { scale: 0, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 300,
        damping: 20,
        delay: 0.5,
      },
    },
  };

  const innerFillVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 0.15, 
      transition: { delay: 0.6, duration: 0.4 } 
    },
  };

  const highlightVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 0.6, 
      transition: { delay: 0.7, duration: 0.3 } 
    },
  };

  const wave1Variants: Variants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: { 
      pathLength: 1, 
      opacity: 0.7, 
      transition: { delay: 0.8, duration: 0.4 } 
    },
  };

  const wave2Variants: Variants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: { 
      pathLength: 1, 
      opacity: 0.5, 
      transition: { delay: 0.9, duration: 0.4 } 
    },
  };

  const arrowVariants: Variants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: { 
      pathLength: 1, 
      opacity: 0.9, 
      transition: { delay: 1, duration: 0.4 } 
    },
  };
  
  return (
    <motion.div 
      className={`flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
      role="presentation"
      variants={shouldAnimate ? containerVariants : undefined}
      initial={shouldAnimate ? "hidden" : undefined}
      animate={shouldAnimate ? "visible" : undefined}
    >
      <svg
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
      >
        {/* Outer guidance ring - represents awareness/environment scanning */}
        <motion.circle
          cx="100"
          cy="100"
          r="90"
          stroke={tertiaryColor}
          strokeWidth="2"
          strokeDasharray="8 4"
          variants={shouldAnimate ? outerRingVariants : undefined}
        />
        
        {/* Middle guidance ring */}
        <motion.circle
          cx="100"
          cy="100"
          r="70"
          stroke={secondaryColor}
          strokeWidth="2.5"
          strokeDasharray="12 6"
          variants={shouldAnimate ? middleRingVariants : undefined}
        />
        
        {/* Inner solid ring - core guidance */}
        <motion.circle
          cx="100"
          cy="100"
          r="50"
          stroke={primaryColor}
          strokeWidth="3"
          variants={shouldAnimate ? innerRingVariants : undefined}
        />
        
        {/* Central flowing path - abstract doorway/passage */}
        <motion.path
          d="M100 40
             C75 55, 65 75, 65 100
             C65 125, 75 145, 100 160
             C125 145, 135 125, 135 100
             C135 75, 125 55, 100 40Z"
          fill="none"
          stroke={primaryColor}
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
          variants={shouldAnimate ? pathVariants : undefined}
        />
        
        {/* Inner path detail - suggests forward movement */}
        <motion.path
          d="M100 60
             C85 70, 80 85, 80 100
             C80 115, 85 130, 100 140
             C115 130, 120 115, 120 100
             C120 85, 115 70, 100 60Z"
          fill={primaryColor}
          variants={shouldAnimate ? innerFillVariants : undefined}
        />
        
        {/* Central beacon/core - the guiding point */}
        <motion.circle
          cx="100"
          cy="100"
          r="12"
          fill={primaryColor}
          variants={shouldAnimate ? beaconVariants : undefined}
        />
        
        {/* Inner beacon highlight */}
        <motion.circle
          cx="100"
          cy="96"
          r="4"
          fill="white"
          variants={shouldAnimate ? highlightVariants : undefined}
        />
        
        {/* Sound/voice wave lines emanating upward - subtle voice integration */}
        <motion.path
          d="M85 70 Q100 55, 115 70"
          stroke={secondaryColor}
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
          variants={shouldAnimate ? wave1Variants : undefined}
        />
        <motion.path
          d="M78 55 Q100 35, 122 55"
          stroke={tertiaryColor}
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
          variants={shouldAnimate ? wave2Variants : undefined}
        />
        
        {/* Directional indicator - forward arrow suggestion */}
        <motion.path
          d="M100 140 L100 165 M90 155 L100 165 L110 155"
          stroke={primaryColor}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          variants={shouldAnimate ? arrowVariants : undefined}
        />
      </svg>
    </motion.div>
  );
}
