'use client';

import React from 'react';

interface MarqueeButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  className?: string;
  type?: 'button' | 'submit';
}

export default function MarqueeButton({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  className = '',
  type = 'button',
}: MarqueeButtonProps) {
  const baseStyles = `
    relative overflow-hidden
    px-8 py-4
    font-bold uppercase tracking-wider
    text-base md:text-lg
    rounded-lg
    transition-all duration-300
    disabled:opacity-50 disabled:cursor-not-allowed
    hover:scale-105 hover:brightness-110
    ${className}
  `;

  const variantStyles = {
    primary: `
      bg-[var(--color-cyan)]
      text-[var(--color-dark)]
      shadow-[var(--glow-cyan)]
    `,
    secondary: `
      bg-[var(--color-purple)]
      text-white
      shadow-[var(--glow-purple)]
    `,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles[variant]}`}
    >
      {/* Marquee Light Border Animation */}
      <span
        className="absolute inset-0 rounded-lg opacity-75 animate-marquee-spin"
        style={{
          background: `
            linear-gradient(90deg,
              transparent 0%,
              transparent 25%,
              ${variant === 'primary' ? 'rgba(255,255,255,0.8)' : 'rgba(0,228,255,0.8)'} 50%,
              transparent 75%,
              transparent 100%
            )
          `,
          backgroundSize: '200% 100%',
          animation: 'marquee 3s linear infinite',
          mixBlendMode: 'overlay',
        }}
      />

      {/* Content */}
      <span className="relative z-10">{children}</span>

      {/* Hover Glow */}
      <span
        className="absolute inset-0 rounded-lg opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none"
        style={{
          background: variant === 'primary'
            ? 'radial-gradient(circle at center, rgba(0,228,255,0.3) 0%, transparent 70%)'
            : 'radial-gradient(circle at center, rgba(47,16,183,0.3) 0%, transparent 70%)',
        }}
      />
    </button>
  );
}
