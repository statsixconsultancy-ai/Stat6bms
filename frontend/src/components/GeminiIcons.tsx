import React from 'react';

export const GeminiSparkleIcon: React.FC<{ size?: number; className?: string }> = ({ size = 18, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={`inline-block flex-shrink-0 ${className}`}
  >
    <path
      d="M12 2C12 7.52285 7.52285 12 2 12C7.52285 12 12 16.4771 12 22C12 16.4771 16.4771 12 22 12C16.4771 12 12 7.52285 12 2Z"
      fill="url(#gemini-sparkle-gradient)"
    />
    <defs>
      <linearGradient id="gemini-sparkle-gradient" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
        <stop stopColor="#4285F4" />
        <stop offset="0.45" stopColor="#9B72CF" />
        <stop offset="0.85" stopColor="#D96570" />
        <stop offset="1" stopColor="#F4B400" />
      </linearGradient>
    </defs>
  </svg>
);

export const GeminiMiniSparkle: React.FC<{ size?: number; className?: string }> = ({ size = 12, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={`inline-block ${className}`}
  >
    <path
      d="M8 1C8 4.86599 4.86599 8 1 8C4.86599 8 8 11.134 8 15C8 11.134 11.134 8 15 8C11.134 8 8 4.86599 8 1Z"
      fill="url(#mini-gemini-gradient)"
    />
    <defs>
      <linearGradient id="mini-gemini-gradient" x1="1" y1="1" x2="15" y2="15" gradientUnits="userSpaceOnUse">
        <stop stopColor="#60A5FA" />
        <stop offset="0.6" stopColor="#A78BFA" />
        <stop offset="1" stopColor="#F472B6" />
      </linearGradient>
    </defs>
  </svg>
);
