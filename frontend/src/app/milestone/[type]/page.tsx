'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { authAPI } from '@/lib/api';

/**
 * Milestone Video Page - Gen Z Bold Design
 *
 * Displays milestone celebration video with:
 * - "LET'S GO!!!" + Artist name in massive brutalist typography
 * - Centered video player with neon border frame
 * - Auto-redirect to HOW IT WORKS when video ends
 * - Marks milestone as viewed so it won't play again
 */

interface MilestoneData {
  has_pending: boolean;
  milestone_type: string | null;
  video_url: string | null;
  description?: string;
  artist_name: string;
}

export default function MilestonePage() {
  const params = useParams();
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);

  const [milestoneData, setMilestoneData] = useState<MilestoneData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [videoEnded, setVideoEnded] = useState(false);

  const milestoneType = params.type as string;

  useEffect(() => {
    const fetchMilestone = async () => {
      try {
        // Get user_id from localStorage
        const token = localStorage.getItem('auth_token');
        if (!token) {
          router.push('/pricing');
          return;
        }

        // Decode JWT to get user_id (simple base64 decode of payload)
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        const userId = decoded.user_id || decoded.sub;

        if (!userId) {
          router.push('/pricing');
          return;
        }

        // Fetch milestone data
        const response = await authAPI.checkMilestones(userId);
        const data = response.data as MilestoneData;

        if (!data.has_pending || data.milestone_type !== milestoneType) {
          // No pending milestone or wrong type - redirect to next step
          router.push('/onboarding/how-it-works');
          return;
        }

        setMilestoneData(data);
      } catch (err) {
        console.error('Error fetching milestone:', err);
        setError('Failed to load milestone');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMilestone();
  }, [milestoneType, router]);

  const handleVideoEnd = async () => {
    setVideoEnded(true);

    try {
      // Get user_id again
      const token = localStorage.getItem('auth_token');
      if (token && milestoneData) {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        const userId = decoded.user_id || decoded.sub;

        // Mark milestone as viewed
        await authAPI.claimMilestone(userId, milestoneType);
      }
    } catch (err) {
      console.error('Error claiming milestone:', err);
    }

    // Redirect to HOW IT WORKS after short delay
    setTimeout(() => {
      router.push('/onboarding/how-it-works');
    }, 1500);
  };

  const handleSkip = async () => {
    // Allow skip but still mark as viewed
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        const userId = decoded.user_id || decoded.sub;
        await authAPI.claimMilestone(userId, milestoneType);
      }
    } catch (err) {
      console.error('Error claiming milestone:', err);
    }
    router.push('/onboarding/how-it-works');
  };

  if (isLoading) {
    return (
      <main className="relative flex min-h-screen w-full items-center justify-center bg-black">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-fuchsia-500 border-t-transparent" />
      </main>
    );
  }

  if (error || !milestoneData) {
    return (
      <main className="relative flex min-h-screen w-full items-center justify-center bg-black">
        <div className="text-center">
          <p className="text-xl text-red-500">{error || 'Milestone not found'}</p>
          <button
            onClick={() => router.push('/onboarding/how-it-works')}
            className="mt-4 border-2 border-white px-6 py-2 font-bold text-white hover:bg-white hover:text-black"
          >
            Continue
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="relative min-h-screen w-full overflow-hidden bg-black">
      {/* Noise texture overlay */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Animated background glow */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-fuchsia-500/20 blur-[128px]" />
        <div className="absolute -right-1/4 bottom-1/4 h-96 w-96 animate-pulse rounded-full bg-cyan-400/20 blur-[128px]" style={{ animationDelay: '1s' }} />
        <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 animate-pulse rounded-full bg-lime-400/10 blur-[100px]" style={{ animationDelay: '0.5s' }} />
      </div>

      {/* Content */}
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 py-12">

        {/* Logo */}
        <div className="mb-8">
          <Image
            src="/n-logo.png"
            alt="NOiSEMaKER"
            width={80}
            height={80}
            className="h-16 w-16 md:h-20 md:w-20"
          />
        </div>

        {/* LET'S GO!!! Header */}
        <div className="mb-8 text-center">
          <h1 className="animate-pulse text-[3rem] font-black uppercase leading-none tracking-tighter text-white md:text-[5rem] lg:text-[7rem]">
            LET&apos;S GO!!!
          </h1>
          <h2 className="mt-4 bg-gradient-to-r from-fuchsia-500 via-cyan-400 to-lime-400 bg-clip-text text-[2rem] font-black uppercase tracking-tight text-transparent md:text-[3rem] lg:text-[4rem]">
            {milestoneData.artist_name}
          </h2>
        </div>

        {/* Video Container - sized for vertical video */}
        <div className="relative w-full max-w-sm md:max-w-md">
          {/* Neon border frame */}
          <div className="absolute -inset-1 rounded-lg bg-gradient-to-r from-fuchsia-500 via-cyan-400 to-lime-400 opacity-75 blur-sm" />
          <div className="absolute -inset-0.5 rounded-lg bg-gradient-to-r from-fuchsia-500 via-cyan-400 to-lime-400" />

          {/* Video */}
          <div className="relative overflow-hidden rounded-lg bg-black">
            {milestoneData.video_url ? (
              <video
                ref={videoRef}
                src={milestoneData.video_url}
                controls
                playsInline
                onEnded={handleVideoEnd}
                className="w-full max-h-[80vh]"
                style={{ aspectRatio: '9/16' }}
              />
            ) : (
              <div className="flex aspect-video items-center justify-center bg-gray-900">
                <p className="text-gray-500">Video unavailable</p>
              </div>
            )}
          </div>
        </div>

        {/* Post-video message */}
        {videoEnded && (
          <div className="mt-8 animate-bounce text-center">
            <p className="text-xl font-bold uppercase tracking-wider text-lime-400">
              Redirecting to setup...
            </p>
          </div>
        )}

        {/* Skip button */}
        {!videoEnded && (
          <button
            onClick={handleSkip}
            className="mt-8 text-sm text-gray-500 underline transition-colors hover:text-white"
          >
            Skip video
          </button>
        )}

        {/* Milestone description */}
        {milestoneData.description && (
          <p className="mt-6 max-w-md text-center text-sm text-gray-400">
            {milestoneData.description}
          </p>
        )}
      </div>
    </main>
  );
}
