'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';

interface PlatformIconProps {
  platform: {
    id: string;
    name: string;
    icon: string;
  };
  selected: boolean;
  disabled: boolean;
  onClick: () => void;
}

// Map platform IDs to actual PNG files in public folder
const platformLogos: { [key: string]: string } = {
  instagram: '/instagram_logo.PNG',
  twitter: '/x_logo.PNG',
  facebook: '/facebook_logo.PNG',
  tiktok: '/tiktok_logo.PNG',
  youtube: '/youtube_logo.PNG',
  reddit: '/reddit_logo.PNG',
  discord: '/discord_logo.PNG',
  threads: '/threads_logo.PNG',
};

export default function PlatformIcon({
  platform,
  selected,
  disabled,
  onClick,
}: PlatformIconProps) {
  const logoSrc = platformLogos[platform.id];

  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.05 } : {}}
      whileTap={!disabled ? { scale: 0.95 } : {}}
      onClick={onClick}
      disabled={disabled}
      className={`
        p-6 rounded-xl transition-all border-2 flex flex-col items-center justify-center
        ${
          selected
            ? 'bg-purple-500/20 border-purple-500 shadow-lg glow'
            : disabled
            ? 'bg-slate-900 border-slate-800 opacity-30 cursor-not-allowed'
            : 'bg-slate-900 border-slate-800 hover:border-purple-500/50 glass cursor-pointer'
        }
      `}
    >
      <div
        className={`w-16 h-16 mb-3 flex items-center justify-center ${
          selected ? '' : disabled ? 'grayscale opacity-50' : ''
        }`}
      >
        {logoSrc ? (
          <Image
            src={logoSrc}
            alt={platform.name}
            width={48}
            height={48}
            className="object-contain"
          />
        ) : (
          <span className="text-4xl">{getPlatformEmoji(platform.id)}</span>
        )}
      </div>
      <p className={`text-white font-semibold text-sm ${disabled ? 'opacity-50' : ''}`}>
        {platform.name}
      </p>
    </motion.button>
  );
}

// Fallback emoji mapping
function getPlatformEmoji(platformId: string): string {
  const emojiMap: { [key: string]: string } = {
    instagram: '📷',
    twitter: '🐦',
    facebook: '📘',
    tiktok: '🎵',
    youtube: '🎥',
    reddit: '🤖',
    discord: '💬',
    threads: '🧵',
  };
  return emojiMap[platformId] || '🔗';
}
