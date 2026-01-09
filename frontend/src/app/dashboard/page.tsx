'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';

/**
 * DASHBOARD - Main hub for NOiSEMaKER users
 *
 * Links to:
 * - Frank's Garage (AI Art Marketplace)
 * - Songs management (future)
 * - Analytics (future)
 */

export default function Dashboard() {
  const [userName, setUserName] = useState<string>('Artist');

  // Get user name from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setUserName(payload.name || 'Artist');
        } catch {
          setUserName('Artist');
        }
      }
    }
  }, []);

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
        <header className="flex items-center justify-between border-b-4 border-white px-4 py-4 md:px-8">
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

          <button
            onClick={() => {
              // Clear all auth tokens
              localStorage.removeItem('auth_token');
              localStorage.removeItem('user_tier');
              document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
              // Redirect to home
              window.location.href = '/';
            }}
            className="border-2 border-white bg-transparent px-4 py-2 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-white hover:text-black"
          >
            Sign Out
          </button>
        </header>

        {/* Welcome */}
        <section className="border-b-4 border-fuchsia-500 bg-fuchsia-500 px-4 py-8 md:px-8 md:py-12">
          <div className="mx-auto max-w-7xl">
            <p className="text-sm font-bold uppercase tracking-widest text-black/70">
              Welcome back,
            </p>
            <h1 className="text-4xl font-black uppercase leading-none tracking-tighter text-black md:text-6xl lg:text-7xl">
              {userName}
            </h1>
          </div>
        </section>

        {/* Dashboard Grid */}
        <section className="px-4 py-8 md:px-8 md:py-12">
          <div className="mx-auto max-w-7xl">
            <h2 className="mb-6 text-sm font-black uppercase tracking-widest text-white/50">
              Your Tools
            </h2>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Frank's Garage Card */}
              <Link
                href="/dashboard/garage"
                className="group border-4 border-fuchsia-500 bg-black p-6 transition-all hover:bg-fuchsia-500/10"
              >
                <div className="text-5xl font-black text-fuchsia-500">
                  01
                </div>
                <h3 className="mt-2 text-2xl font-black uppercase text-white">
                  Frank&apos;s Garage
                </h3>
                <p className="mt-2 text-sm text-white/50">
                  AI-generated album art marketplace. Download free with tokens or purchase exclusive artwork.
                </p>
                <div className="mt-4 flex items-center gap-2 text-sm font-bold text-fuchsia-500">
                  Browse Art
                  <span className="transition-transform group-hover:translate-x-2">→</span>
                </div>
              </Link>

              {/* Songs Card (Coming Soon) */}
              <div className="border-4 border-white/20 bg-black p-6 opacity-50">
                <div className="text-5xl font-black text-white/30">
                  02
                </div>
                <h3 className="mt-2 text-2xl font-black uppercase text-white/50">
                  My Songs
                </h3>
                <p className="mt-2 text-sm text-white/30">
                  Manage your promoted songs and track performance across platforms.
                </p>
                <div className="mt-4 text-sm font-bold text-white/30">
                  Coming Soon
                </div>
              </div>

              {/* Analytics Card (Coming Soon) */}
              <div className="border-4 border-white/20 bg-black p-6 opacity-50">
                <div className="text-5xl font-black text-white/30">
                  03
                </div>
                <h3 className="mt-2 text-2xl font-black uppercase text-white/50">
                  Analytics
                </h3>
                <p className="mt-2 text-sm text-white/30">
                  Track engagement, reach, and growth across all your connected platforms.
                </p>
                <div className="mt-4 text-sm font-bold text-white/30">
                  Coming Soon
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Stats (placeholder) */}
        <section className="border-t-4 border-white/20 bg-black px-4 py-8 md:px-8">
          <div className="mx-auto max-w-7xl">
            <h2 className="mb-6 text-sm font-black uppercase tracking-widest text-white/50">
              Quick Stats
            </h2>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="border-2 border-lime-400/30 p-4">
                <div className="text-3xl font-black text-lime-400">--</div>
                <div className="text-xs font-bold uppercase text-white/50">Art Tokens</div>
              </div>
              <div className="border-2 border-cyan-400/30 p-4">
                <div className="text-3xl font-black text-cyan-400">--</div>
                <div className="text-xs font-bold uppercase text-white/50">Songs Active</div>
              </div>
              <div className="border-2 border-fuchsia-500/30 p-4">
                <div className="text-3xl font-black text-fuchsia-500">--</div>
                <div className="text-xs font-bold uppercase text-white/50">Posts This Week</div>
              </div>
              <div className="border-2 border-white/30 p-4">
                <div className="text-3xl font-black text-white">--</div>
                <div className="text-xs font-bold uppercase text-white/50">Platforms</div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t-4 border-white bg-black px-4 py-6 text-center md:px-8">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            NOiSEMaKER by DooWopp
          </p>
        </footer>
      </div>
    </main>
  );
}
