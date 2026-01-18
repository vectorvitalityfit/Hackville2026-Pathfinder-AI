interface PhoneSonarAnimationProps {
  className?: string;
  size?: number;
}

export function PhoneSonarAnimation({ className = "", size = 280 }: PhoneSonarAnimationProps) {
  return (
    <div 
      className={`flex items-center justify-center ${className}`} 
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
      >
        {/* Sonar waves emanating from top of phone */}
        <g>
          {[1, 2, 3].map((i) => (
            <path
              key={i}
              d="M100 50 Q125 25, 150 50"
              stroke="hsl(200, 98%, 39%)"
              strokeWidth="2.5"
              strokeLinecap="round"
              fill="none"
              className="sonar-wave"
              style={{
                animationDelay: `${(i - 1) * 0.4}s`,
                transformOrigin: "100px 50px",
              }}
            />
          ))}
        </g>

        {/* Phone body */}
        <rect
          x="70"
          y="55"
          width="60"
          height="110"
          rx="8"
          stroke="hsl(200, 98%, 39%)"
          strokeWidth="2.5"
          fill="none"
        />

        {/* Phone screen */}
        <rect
          x="75"
          y="65"
          width="50"
          height="85"
          rx="4"
          stroke="hsl(200, 98%, 39%)"
          strokeWidth="1.5"
          fill="hsl(200, 98%, 39%)"
          fillOpacity="0.08"
        />

        {/* Home indicator */}
        <rect
          x="90"
          y="155"
          width="20"
          height="3"
          rx="1.5"
          fill="hsl(200, 98%, 39%)"
          opacity="0.5"
        />
      </svg>

      <style>{`
        @keyframes sonar-expand {
          0% {
            opacity: 0.9;
            transform: scale(1) translateY(0);
          }
          100% {
            opacity: 0;
            transform: scale(1.6) translateY(-12px);
          }
        }
        
        .sonar-wave {
          animation: sonar-expand 1.4s ease-out infinite;
        }
      `}</style>
    </div>
  );
}