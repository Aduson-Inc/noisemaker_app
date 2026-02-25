'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { platformAPI } from '@/lib/api';

const PLATFORM_META: Record<string, { name: string; logo: string }> = {
  instagram: { name: 'Instagram', logo: '/instagram_logo.PNG' },
  twitter: { name: 'Twitter/X', logo: '/x_logo.PNG' },
  facebook: { name: 'Facebook', logo: '/facebook_logo.PNG' },
  tiktok: { name: 'TikTok', logo: '/tiktok_logo.PNG' },
  youtube: { name: 'YouTube', logo: '/youtube_logo.PNG' },
  reddit: { name: 'Reddit', logo: '/reddit_logo.PNG' },
  discord: { name: 'Discord', logo: '/discord_logo.PNG' },
  threads: { name: 'Threads', logo: '/threads_logo.PNG' },
};

function CallbackHandler() {
  const searchParams = useSearchParams();
  const params = useParams();
  const router = useRouter();

  const [status, setStatus] = useState<'connecting' | 'success' | 'error'>('connecting');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const platform = params.platform as string;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const meta = PLATFORM_META[platform] || { name: platform, logo: '' };

  useEffect(() => {
    const processCallback = async () => {
      // Extract user_id from JWT in localStorage
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setStatus('error');
        setErrorMessage('Session expired. Please sign in again.');
        setTimeout(() => router.replace('/'), 3000);
        return;
      }

      let userId: string;
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        userId = payload.sub || payload.user_id;
        if (!userId) throw new Error('No user_id');
      } catch {
        setStatus('error');
        setErrorMessage('Invalid session. Redirecting...');
        setTimeout(() => router.replace('/'), 3000);
        return;
      }

      if (!code || !state) {
        setStatus('error');
        setErrorMessage('Missing authorization data. The platform did not return the required parameters.');
        return;
      }

      try {
        const response = await platformAPI.handleCallback(platform, code, userId, state);
        if (response.data.success) {
          setStatus('success');
          // Brief success flash before redirect
          setTimeout(() => router.replace('/onboarding/platforms'), 1200);
        } else {
          setStatus('error');
          setErrorMessage('Platform denied the connection. Please try again.');
        }
      } catch (err: any) {
        setStatus('error');
        const detail = err?.response?.data?.detail;
        setErrorMessage(detail || 'Connection failed. Please try again.');
      }
    };

    processCallback();
  }, [code, state, platform, router]);

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">
      {/* Noise texture — matches platforms page */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10">
        {/* Header — same as platforms page */}
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

        {/* Divider */}
        <div className="border-b-4 border-white" />

        {/* Content */}
        <div className="flex min-h-[70vh] flex-col items-center justify-center px-6">

          {status === 'connecting' && (
            <div className="flex flex-col items-center gap-8">
              {/* Platform logo with pulse ring */}
              <div className="relative">
                <div className="absolute inset-0 animate-ping rounded-full border-2 border-lime-400 opacity-20"
                     style={{ margin: '-12px', animationDuration: '2s' }} />
                <div className="relative h-20 w-20 md:h-24 md:w-24">
                  {meta.logo && (
                    <Image
                      src={meta.logo}
                      alt={meta.name}
                      fill
                      className="object-contain"
                    />
                  )}
                </div>
              </div>

              {/* Spinner */}
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-lime-400 border-t-transparent" />

              {/* Text */}
              <div className="text-center">
                <h1 className="text-3xl font-black uppercase tracking-tighter text-white md:text-4xl">
                  Connecting <span className="text-lime-400">{meta.name}</span>
                </h1>
                <p className="mt-2 text-xs font-bold uppercase tracking-widest text-gray-500">
                  Securing your connection
                </p>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="flex flex-col items-center gap-6">
              {/* Platform logo */}
              <div className="relative h-20 w-20 md:h-24 md:w-24">
                {meta.logo && (
                  <Image
                    src={meta.logo}
                    alt={meta.name}
                    fill
                    className="object-contain"
                  />
                )}
              </div>

              {/* Success badge */}
              <div className="flex items-center gap-2 border-4 border-lime-400 bg-lime-400 px-6 py-3">
                <span className="text-xl font-black uppercase tracking-tight text-black">
                  ✓ {meta.name} Connected
                </span>
              </div>

              <p className="text-xs font-bold uppercase tracking-widest text-gray-500">
                Redirecting...
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="flex flex-col items-center gap-6">
              {/* Platform logo — desaturated */}
              <div className="relative h-20 w-20 opacity-40 grayscale md:h-24 md:w-24">
                {meta.logo && (
                  <Image
                    src={meta.logo}
                    alt={meta.name}
                    fill
                    className="object-contain"
                  />
                )}
              </div>

              {/* Error title */}
              <h1 className="text-3xl font-black uppercase tracking-tighter text-white md:text-4xl">
                Connection <span className="text-red-400">Failed</span>
              </h1>

              {/* Error message */}
              <div className="max-w-md border-l-4 border-red-500 bg-red-500/10 px-4 py-3">
                <p className="text-sm font-bold text-red-400">{errorMessage}</p>
              </div>

              {/* Back button */}
              <button
                onClick={() => router.replace('/onboarding/platforms')}
                className="border-4 border-white px-8 py-3 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-white hover:text-black"
              >
                ← Back to Platforms
              </button>
            </div>
          )}
        </div>

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

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="relative min-h-screen w-full bg-black flex items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-lime-400 border-t-transparent" />
        </main>
      }
    >
      <CallbackHandler />
    </Suspense>
  );
}
