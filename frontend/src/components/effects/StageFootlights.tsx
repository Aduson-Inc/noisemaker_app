'use client';

import Image from 'next/image';
import { useEffect, useState } from 'react';

interface Platform {
  name: string;
  logoPath: string;
}

const platforms: Platform[] = [
  { name: 'Discord', logoPath: '/discord_logo.PNG' },
  { name: 'YouTube', logoPath: '/youtube_logo.PNG' },
  { name: 'Threads', logoPath: '/threads_logo.PNG' },
  { name: 'Facebook', logoPath: '/facebook_logo.PNG' },
  { name: 'Instagram', logoPath: '/instagram_logo.PNG' },
  { name: 'Reddit', logoPath: '/reddit_logo.PNG' },
  { name: 'TikTok', logoPath: '/tiktok_logo.PNG' },
  { name: 'X', logoPath: '/x_logo.PNG' },
];

interface StageFootlightsProps {
  visible?: boolean;
  className?: string;
}

export default function StageFootlights({ visible = true, className = '' }: StageFootlightsProps) {
  const [glowPhases, setGlowPhases] = useState<number[]>(
    platforms.map(() => Math.random() * Math.PI * 2)
  );

  useEffect(() => {
    if (!visible) return;

    // Animate pulsing glow for each platform
    const interval = setInterval(() => {
      setGlowPhases((prev) =>
        prev.map((phase) => (phase + 0.05) % (Math.PI * 2))
      );
    }, 50);

    return () => clearInterval(interval);
  }, [visible]);

  if (!visible) return null;

  return (
    <div className={`fixed bottom-0 left-0 right-0 z-20 pointer-events-none ${className}`}>
      {/* Stage Edge Line */}
      <div
        className="absolute bottom-16 left-0 right-0 h-1 opacity-30"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, var(--color-cyan) 50%, transparent 100%)',
        }}
      />

      {/* Footlights Container */}
      <div className="flex justify-center items-end gap-4 md:gap-8 px-4 pb-4">
        {platforms.map((platform, index) => {
          const glowIntensity = Math.sin(glowPhases[index]) * 0.3 + 0.5; // 0.2 to 0.8
          const colors = [
            'rgba(0, 228, 255, {{intensity}})', // Cyan
            'rgba(216, 36, 211, {{intensity}})', // Magenta
            'rgba(47, 16, 183, {{intensity}})', // Purple
          ];
          const glowColor = colors[index % 3].replace('{{intensity}}', glowIntensity.toString());

          return (
            <div key={platform.name} className="relative group">
              {/* Light Beam (upward) */}
              <div
                className="absolute bottom-0 left-1/2 -translate-x-1/2 w-20 h-32 opacity-20"
                style={{
                  background: `linear-gradient(to top, ${glowColor} 0%, transparent 100%)`,
                  filter: 'blur(15px)',
                  transition: 'opacity 0.5s ease',
                }}
              />

              {/* Platform Logo */}
              <div
                className="relative w-12 h-12 md:w-14 md:h-14 rounded-full bg-black/50 backdrop-blur-sm border border-white/10 flex items-center justify-center transition-all duration-300 hover:scale-110"
                style={{
                  boxShadow: `0 0 20px ${glowColor}`,
                }}
              >
                <div className="relative w-8 h-8 md:w-10 md:h-10">
                  <Image
                    src={platform.logoPath}
                    alt={platform.name}
                    fill
                    className="object-contain p-1"
                    sizes="40px"
                  />
                </div>

                {/* Inner Glow */}
                <div
                  className="absolute inset-0 rounded-full"
                  style={{
                    background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
                    filter: 'blur(8px)',
                  }}
                />
              </div>

              {/* Platform Name Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="bg-black/80 backdrop-blur-sm px-2 py-1 rounded text-xs text-white whitespace-nowrap">
                  {platform.name}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
