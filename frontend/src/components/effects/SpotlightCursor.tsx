'use client';

import { useEffect, useState } from 'react';

interface SpotlightCursorProps {
  enabled?: boolean;
  color?: 'cyan' | 'magenta' | 'purple';
  size?: number;
  intensity?: number;
}

export default function SpotlightCursor({
  enabled = true,
  color = 'cyan',
  size = 300,
  intensity = 0.4,
}: SpotlightCursorProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isMobile, setIsMobile] = useState(false);
  const [autoPosition, setAutoPosition] = useState({ x: 50, y: 50 });

  // Detect mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Track mouse position on desktop
  useEffect(() => {
    if (isMobile || !enabled) return;

    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [isMobile, enabled]);

  // Auto-animate spotlight on mobile
  useEffect(() => {
    if (!isMobile || !enabled) return;

    const animate = () => {
      const time = Date.now() / 2000; // Slow animation
      const x = 50 + Math.sin(time) * 20; // Oscillate 30-70%
      const y = 50 + Math.cos(time * 0.7) * 15; // Oscillate 35-65%
      setAutoPosition({ x, y });
    };

    const interval = setInterval(animate, 50);
    return () => clearInterval(interval);
  }, [isMobile, enabled]);

  if (!enabled) return null;

  const colorMap = {
    cyan: 'rgba(0, 228, 255, {{intensity}})',
    magenta: 'rgba(216, 36, 211, {{intensity}})',
    purple: 'rgba(47, 16, 183, {{intensity}})',
  };

  const spotlightColor = colorMap[color].replace('{{intensity}}', intensity.toString());

  return (
    <>
      {/* Spotlight Effect */}
      <div
        className="fixed inset-0 pointer-events-none z-10 transition-opacity duration-300"
        style={{
          background: isMobile
            ? `radial-gradient(circle ${size}px at ${autoPosition.x}% ${autoPosition.y}%, ${spotlightColor} 0%, transparent 60%)`
            : `radial-gradient(circle ${size}px at ${mousePosition.x}px ${mousePosition.y}px, ${spotlightColor} 0%, transparent 60%)`,
          mixBlendMode: 'screen',
        }}
      />

      {/* Secondary Glow (softer, larger) */}
      <div
        className="fixed inset-0 pointer-events-none z-9 transition-opacity duration-500"
        style={{
          background: isMobile
            ? `radial-gradient(circle ${size * 2}px at ${autoPosition.x}% ${autoPosition.y}%, ${spotlightColor.replace(intensity.toString(), (intensity * 0.3).toString())} 0%, transparent 70%)`
            : `radial-gradient(circle ${size * 2}px at ${mousePosition.x}px ${mousePosition.y}px, ${spotlightColor.replace(intensity.toString(), (intensity * 0.3).toString())} 0%, transparent 70%)`,
          filter: 'blur(40px)',
          mixBlendMode: 'screen',
        }}
      />
    </>
  );
}
