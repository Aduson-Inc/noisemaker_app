'use client';

import PlatformOrb from './PlatformOrb';
import { useInView } from 'react-intersection-observer';

interface Platform {
  name: string;
  logoPath: string;
  glowColor: 'cyan' | 'magenta' | 'purple';
}

const platforms: Platform[] = [
  { name: 'Discord', logoPath: '/discord_logo.PNG', glowColor: 'purple' },
  { name: 'YouTube', logoPath: '/youtube_logo.PNG', glowColor: 'cyan' },
  { name: 'Threads', logoPath: '/threads_logo.PNG', glowColor: 'magenta' },
  { name: 'Facebook', logoPath: '/facebook_logo.PNG', glowColor: 'cyan' },
  { name: 'Instagram', logoPath: '/instagram_logo.PNG', glowColor: 'magenta' },
  { name: 'Reddit', logoPath: '/reddit_logo.PNG', glowColor: 'purple' },
  { name: 'TikTok', logoPath: '/tiktok_logo.PNG', glowColor: 'cyan' },
  { name: 'X', logoPath: '/x_logo.PNG', glowColor: 'magenta' },
];

interface PlatformShowcaseProps {
  layout?: 'grid' | 'row';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function PlatformShowcase({
  layout = 'grid',
  size = 'md',
  className = '',
}: PlatformShowcaseProps) {
  const { ref, inView } = useInView({
    threshold: 0.2,
    triggerOnce: true,
  });

  return (
    <div ref={ref} className={`${className}`}>
      {/* Heading */}
      <h3 className="text-center text-2xl md:text-3xl font-bold uppercase tracking-wider text-white mb-8">
        8 PLATFORMS. ONE SYSTEM.
      </h3>

      {/* Platform Grid/Row */}
      <div
        className={
          layout === 'grid'
            ? 'grid grid-cols-4 gap-8 md:gap-12 max-w-4xl mx-auto'
            : 'flex justify-center items-center gap-6 md:gap-8 flex-wrap'
        }
      >
        {platforms.map((platform, index) => (
          <div
            key={platform.name}
            className={`
              flex justify-center
              transition-all duration-500
              ${inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
            `}
            style={{
              transitionDelay: `${index * 100}ms`,
            }}
          >
            <PlatformOrb
              platform={platform.name}
              logoPath={platform.logoPath}
              size={size}
              glowColor={platform.glowColor}
            />
          </div>
        ))}
      </div>

      {/* Subtext */}
      <p className="text-center text-gray-400 text-sm md:text-base mt-12 max-w-2xl mx-auto">
        YOUR MUSIC AUTOMATICALLY PROMOTED ACROSS ALL MAJOR SOCIAL PLATFORMS.
        <br />
        <span className="text-[var(--color-cyan)] font-bold">
          NO MANUAL POSTING. NO HEADACHES. JUST RESULTS.
        </span>
      </p>
    </div>
  );
}
