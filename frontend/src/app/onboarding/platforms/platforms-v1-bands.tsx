'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { platformAPI } from '@/lib/api';

/**
 * VARIANT 1: "HORIZONTAL BANDS"
 *
 * Full-width horizontal bands for each platform (magazine editorial style).
 * Click band to initiate OAuth → returns with "Connected" badge.
 * Matching the pricing page aesthetic with numbered rows.
 *
 * UNIFIED FLOW: Select + Connect in one action
 * - Click platform → OAuth redirect → return with connected status
 * - Tier limit strictly enforced
 * - Minimum 1 connection to proceed
 */

interface Platform {
  id: string;
  name: string;
  logo: string;
  description: string;
}

interface PlatformConnection {
  connected: boolean;
  username?: string;
  account_type?: string;
}

const PLATFORMS: Platform[] = [
  { id: 'instagram', name: 'Instagram', logo: '/instagram_logo.PNG', description: 'Stories, Reels, Posts' },
  { id: 'twitter', name: 'Twitter/X', logo: '/x_logo.PNG', description: 'Tweets, Threads' },
  { id: 'facebook', name: 'Facebook', logo: '/facebook_logo.PNG', description: 'Posts, Stories' },
  { id: 'tiktok', name: 'TikTok', logo: '/tiktok_logo.PNG', description: 'Short-form Videos' },
  { id: 'youtube', name: 'YouTube', logo: '/youtube_logo.PNG', description: 'Shorts, Community' },
  { id: 'reddit', name: 'Reddit', logo: '/reddit_logo.PNG', description: 'Subreddit Posts' },
  { id: 'discord', name: 'Discord', logo: '/discord_logo.PNG', description: 'Server Announcements' },
  { id: 'threads', name: 'Threads', logo: '/threads_logo.PNG', description: 'Text Posts' },
];

const TIER_COLORS = {
  pending: {
    bg: 'bg-white',
    text: 'text-white',
    border: 'border-white',
    hex: '#ffffff'
  },
  talent: {
    bg: 'bg-cyan-400',
    text: 'text-cyan-400',
    border: 'border-cyan-400',
    hex: '#22d3ee'
  },
  star: {
    bg: 'bg-fuchsia-500',
    text: 'text-fuchsia-500',
    border: 'border-fuchsia-500',
    hex: '#d946ef'
  },
  legend: {
    bg: 'bg-lime-400',
    text: 'text-lime-400',
    border: 'border-lime-400',
    hex: '#a3e635'
  },
};

export default function PlatformsBandsV1() {
  const router = useRouter();

  const [connections, setConnections] = useState<Record<string, PlatformConnection>>({});
  const [platformLimit, setPlatformLimit] = useState<number>(2);
  const [tier, setTier] = useState<'pending' | 'talent' | 'star' | 'legend'>('talent');
  const [isLoading, setIsLoading] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getUserId = (): string | null => {
    if (typeof window === 'undefined') return null;
    const token = localStorage.getItem('auth_token');
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.sub || payload.user_id || null;
    } catch {
      return null;
    }
  };

  // Fetch connection status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      const userId = getUserId();
      if (!userId) {
        setError('Please sign in to continue');
        setIsLoading(false);
        return;
      }

      try {
        const response = await platformAPI.getConnectionsStatus(userId);
        const data = response.data;

        // Transform connection objects to PlatformConnection objects
        // Backend returns {platform: {connected: bool, username: string, ...}}
        const transformedConnections: Record<string, PlatformConnection> = {};
        if (data.connections) {
          for (const [platform, connectionData] of Object.entries(data.connections)) {
            const conn = connectionData as { connected?: boolean; username?: string; account_type?: string };
            transformedConnections[platform] = {
              connected: Boolean(conn?.connected),
              username: conn?.username,
              account_type: conn?.account_type
            };
          }
        }
        setConnections(transformedConnections);
        setPlatformLimit(data.platform_limit || 2);
        setTier(data.subscription_tier || 'talent');
      } catch (err) {
        console.error('Error fetching platform status:', err);
        setError('Failed to load platform status');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, []);

  // Count connected platforms
  const connectedCount = Object.values(connections).filter(c => c.connected).length;
  const canConnectMore = connectedCount < platformLimit;
  const canContinue = connectedCount >= 1;

  // Handle platform connection
  const handleConnect = async (platformId: string) => {
    const userId = getUserId();
    if (!userId) {
      setError('Please sign in to continue');
      return;
    }

    // SECURITY CHECK: Enforce tier limit
    if (connectedCount >= platformLimit) {
      setError(`You've reached your ${tier.toUpperCase()} tier limit of ${platformLimit} platforms`);
      return;
    }

    // Already connected?
    if (connections[platformId]?.connected) {
      return;
    }

    setConnectingPlatform(platformId);
    setError(null);

    try {
      const response = await platformAPI.getAuthUrl(platformId, userId);
      const { auth_url } = response.data;

      if (auth_url) {
        // Redirect to OAuth
        window.location.href = auth_url;
      } else {
        throw new Error('No auth URL received');
      }
    } catch (err) {
      console.error('Error getting auth URL:', err);
      setError(`Failed to connect ${platformId}. Please try again.`);
      setConnectingPlatform(null);
    }
  };

  const handleContinue = () => {
    if (canContinue) {
      router.push('/onboarding/how-it-works-2');
    }
  };

  const tierColors = TIER_COLORS[tier];

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">
      {/* Noise texture */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 md:px-12 md:py-6">
          <Link href="/" className="flex items-center gap-2">
            <Image
              src="/n-logo.png"
              alt="NOiSEMaKER"
              width={40}
              height={40}
              className="h-8 w-8 md:h-10 md:w-10"
            />
            <span className="text-lg font-black uppercase tracking-tight text-white">
              NOiSEMaKER
            </span>
          </Link>
          <span className="text-xs font-bold uppercase tracking-widest text-gray-500">
            Step 2 of 4
          </span>
        </header>

        {/* Title Section */}
        <section className="border-b-4 border-white px-6 py-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-4xl font-black uppercase leading-none tracking-tighter text-white md:text-5xl lg:text-6xl">
                CONNECT YOUR
                <br />
                <span className={tierColors.text}>PLATFORMS</span>
              </h1>
            </div>

            {/* Progress Badge */}
            <div className={`inline-flex items-center gap-3 border-4 ${tierColors.border} bg-black px-4 py-3`}>
              <span className={`text-3xl font-black ${tierColors.text}`}>
                {connectedCount}/{platformLimit}
              </span>
              <div className="text-left">
                <p className="text-xs font-bold uppercase tracking-widest text-gray-500">Connected</p>
                <p className={`text-sm font-black uppercase ${tierColors.text}`}>{tier} Tier</p>
              </div>
            </div>
          </div>
        </section>

        {/* Error */}
        {error && (
          <div className="border-b-4 border-red-500 bg-red-500/20 px-6 py-4">
            <p className="font-bold text-red-400">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-1 text-sm text-red-300 underline hover:text-white"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Loading */}
        {isLoading ? (
          <div className="flex items-center justify-center py-24">
            <div className={`h-12 w-12 animate-spin rounded-full border-4 ${tierColors.border} border-t-transparent`} />
          </div>
        ) : (
          /* Platform Bands */
          <div>
            {PLATFORMS.map((platform, index) => {
              const connection = connections[platform.id];
              const isConnected = connection?.connected || false;
              const isConnecting = connectingPlatform === platform.id;
              const isLimitReached = !isConnected && connectedCount >= platformLimit;

              return (
                <button
                  key={platform.id}
                  onClick={() => handleConnect(platform.id)}
                  disabled={isConnected || isConnecting || isLimitReached}
                  className={`group flex w-full items-center justify-between border-b-2 px-6 py-5 text-left transition-all ${
                    isConnected
                      ? `${tierColors.border} border-l-4 bg-gradient-to-r from-black via-black to-transparent`
                      : isLimitReached
                        ? 'cursor-not-allowed border-gray-800 opacity-40'
                        : 'border-white/10 hover:border-white/30 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-4 md:gap-6">
                    {/* Number */}
                    <span className={`text-4xl font-black md:text-5xl ${
                      isConnected ? tierColors.text : 'text-white/20'
                    }`}>
                      0{index + 1}
                    </span>

                    {/* Logo */}
                    <div className="relative h-14 w-14 md:h-16 md:w-16">
                      <Image
                        src={platform.logo}
                        alt={platform.name}
                        fill
                        className={`object-contain transition-all ${
                          isConnected ? '' : isLimitReached ? 'grayscale' : 'group-hover:scale-110'
                        }`}
                      />
                    </div>

                    {/* Info */}
                    <div>
                      <h3 className={`text-xl font-black uppercase md:text-2xl ${
                        isConnected ? tierColors.text : 'text-white'
                      }`}>
                        {platform.name}
                      </h3>
                      {isConnected && connection?.username ? (
                        <p className={`text-sm font-bold ${tierColors.text}`}>
                          @{connection.username}
                        </p>
                      ) : (
                        <p className="text-xs text-gray-500">{platform.description}</p>
                      )}
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center gap-4">
                    {isConnecting ? (
                      <div className="flex items-center gap-2">
                        <div className={`h-5 w-5 animate-spin rounded-full border-2 ${tierColors.border} border-t-transparent`} />
                        <span className="text-xs font-bold uppercase text-gray-400">Connecting...</span>
                      </div>
                    ) : isConnected ? (
                      <span className={`flex items-center gap-2 border-2 ${tierColors.border} ${tierColors.bg} px-4 py-2 text-sm font-black uppercase text-black`}>
                        <span>✓</span> Connected
                      </span>
                    ) : isLimitReached ? (
                      <span className="border-2 border-gray-700 px-4 py-2 text-xs font-black uppercase text-gray-600">
                        Limit Reached
                      </span>
                    ) : (
                      <span className="border-2 border-white/30 px-4 py-2 text-sm font-black uppercase text-white/50 transition-all group-hover:border-white group-hover:bg-white group-hover:text-black">
                        Connect →
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Continue Button - Fixed at bottom */}
        <section className="sticky bottom-0 border-t-4 border-white bg-black px-6 py-4">
          <button
            onClick={handleContinue}
            disabled={!canContinue}
            className={`w-full border-4 py-4 text-lg font-black uppercase tracking-wider transition-all ${
              canContinue
                ? `${tierColors.border} bg-white text-black hover:bg-gray-100`
                : 'cursor-not-allowed border-gray-700 bg-gray-900 text-gray-600'
            }`}
          >
            {!canContinue
              ? 'CONNECT AT LEAST 1 PLATFORM'
              : `CONTINUE → (${connectedCount} CONNECTED)`}
          </button>
        </section>

        {/* Footer */}
        <footer className="border-t-4 border-white/20 bg-black px-6 py-6 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            © 2026 NOiSEMaKER by DooWopp
          </p>
        </footer>
      </div>
    </main>
  );
}
