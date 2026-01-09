'use client';

import { useEffect, useRef } from 'react';

interface WaveformVisualizerProps {
  color?: 'cyan' | 'magenta' | 'purple';
  amplitude?: number;
  frequency?: number;
  lineWidth?: number;
  opacity?: number;
  className?: string;
}

export default function WaveformVisualizer({
  color = 'cyan',
  amplitude = 50,
  frequency = 0.02,
  lineWidth = 3,
  opacity = 0.3,
  className = '',
}: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Color map
    const colorMap = {
      cyan: `rgba(0, 228, 255, ${opacity})`,
      magenta: `rgba(216, 36, 211, ${opacity})`,
      purple: `rgba(47, 16, 183, ${opacity})`,
    };

    const strokeColor = colorMap[color];

    // Animation
    let phase = 0;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerY = canvas.height / 2;

      // Draw multiple waveforms for depth
      for (let layer = 0; layer < 3; layer++) {
        ctx.beginPath();
        ctx.strokeStyle = strokeColor.replace(
          opacity.toString(),
          (opacity * (1 - layer * 0.3)).toString()
        );
        ctx.lineWidth = lineWidth * (1 - layer * 0.2);
        ctx.lineCap = 'round';

        for (let x = 0; x < canvas.width; x += 2) {
          // Create sine wave with varying amplitude
          const y =
            centerY +
            Math.sin(x * frequency + phase + layer * 0.5) *
              amplitude *
              (1 - layer * 0.2) +
            Math.sin(x * frequency * 2 + phase * 1.5 + layer) * (amplitude * 0.3);

          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }

        ctx.stroke();
      }

      // Update phase for animation
      phase += 0.02;

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [color, amplitude, frequency, lineWidth, opacity]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-none ${className}`}
      style={{ mixBlendMode: 'screen' }}
    />
  );
}
