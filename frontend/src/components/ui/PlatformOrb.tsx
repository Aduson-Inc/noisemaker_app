'use client';

import Image from 'next/image';
import { useState } from 'react';

interface PlatformOrbProps {
  platform: string;
  logoPath: string;
  size?: 'sm' | 'md' | 'lg';
  glowColor?: 'cyan' | 'magenta' | 'purple';
  onClick?: () => void;
}

const sizeMap = {
  sm: 'w-16 h-16 md:w-20 md:h-20',
  md: 'w-20 h-20 md:w-24 md:h-24',
  lg: 'w-24 h-24 md:w-32 md:h-32',
};

const glowColorMap = {
  cyan: 'shadow-[var(--glow-cyan)]',
  magenta: 'shadow-[var(--glow-magenta)]',
  purple: 'shadow-[var(--glow-purple)]',
};

export default function PlatformOrb({
  platform,
  logoPath,
  size = 'md',
  glowColor = 'cyan',
  onClick,
}: PlatformOrbProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="relative group cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* Pulsing Glow Ring */}
      <div
        className={`
          absolute inset-0 rounded-full
          ${glowColorMap[glowColor]}
          opacity-60 animate-pulse
          transition-all duration-500
          ${isHovered ? 'scale-110 opacity-100' : 'scale-100'}
        `}
        style={{
          filter: 'blur(10px)',
        }}
      />

      {/* Orb Container */}
      <div
        className={`
          relative
          ${sizeMap[size]}
          rounded-full
          bg-white/10
          backdrop-blur-sm
          border border-white/20
          flex items-center justify-center
          transition-all duration-500 ease-out
          ${isHovered ? 'scale-110 brightness-125 rotate-[5deg]' : 'scale-100'}
        `}
        style={{
          boxShadow: isHovered
            ? `0 0 30px ${glowColor === 'cyan' ? 'rgba(0,228,255,0.8)' : glowColor === 'magenta' ? 'rgba(216,36,211,0.8)' : 'rgba(47,16,183,0.8)'}`
            : '0 0 15px rgba(255,255,255,0.1)',
        }}
      >
        {/* Platform Logo */}
        <div className="relative w-12 h-12 md:w-16 md:h-16">
          <Image
            src={logoPath}
            alt={platform}
            fill
            className="object-contain p-2"
            sizes="(max-width: 768px) 48px, 64px"
          />
        </div>

        {/* Liquid Morph Effect on Hover */}
        {isHovered && (
          <div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-transparent via-white/10 to-transparent animate-pulse pointer-events-none"
            style={{
              animation: 'pulse 1.5s ease-in-out infinite',
            }}
          />
        )}
      </div>

      {/* Platform Label (shows on hover) */}
      <div
        className={`
          absolute -bottom-8 left-1/2 -translate-x-1/2
          whitespace-nowrap
          text-xs uppercase tracking-wider font-bold
          text-white/80
          transition-all duration-300
          ${isHovered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}
        `}
      >
        {platform}
      </div>
    </div>
  );
}
