'use client';

import Image from 'next/image';
import Link from 'next/link';

/**
 * DESIGN 2: Gen Z Bold
 *
 * Anti-corporate, TikTok-native energy
 * - Oversized brutalist typography
 * - High contrast black/white with neon accents
 * - Authentic/raw aesthetic
 * - Bold statements, slightly chaotic layout
 * - Sticker/badge elements
 * - Would go viral on TikTok
 */

export default function GenZLanding() {
  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">

      {/* Noise texture overlay */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Content Container */}
      <div className="relative z-10">

        {/* ========== HEADER ========== */}
        <header className="flex items-center justify-between px-6 py-4 md:px-12 md:py-6">
          <Link href="/" className="group flex items-center gap-2">
            <Image
              src="/doowopp-logo.png"
              alt="DooWopp"
              width={100}
              height={32}
              className="h-6 w-auto brightness-0 invert md:h-8"
            />
          </Link>

          {/* Brutalist Sign In */}
          <Link
            href="/auth/signin"
            className="border-2 border-white bg-transparent px-4 py-2 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-white hover:text-black"
          >
            Sign In
          </Link>
        </header>

        {/* ========== HERO SECTION ========== */}
        <section className="relative px-6 py-16 md:py-24">

          {/* Floating badge - top right */}
          <div className="absolute right-4 top-20 rotate-12 rounded-full border-2 border-lime-400 bg-lime-400 px-4 py-2 text-xs font-black uppercase text-black md:right-12 md:top-24 md:px-6 md:text-sm">
            No fake streams
          </div>

          {/* Main content */}
          <div className="mx-auto max-w-5xl">

            {/* Small N logo */}
            <div className="mb-8 flex items-center gap-4">
              <Image
                src="/n-logo.png"
                alt="N"
                width={60}
                height={60}
                className="h-12 w-12 md:h-16 md:w-16"
              />
              <span className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500">
                by DooWopp
              </span>
            </div>

            {/* MASSIVE headline */}
            <h1 className="mb-4 text-[4rem] font-black uppercase leading-[0.85] tracking-tighter text-white md:text-[8rem] lg:text-[10rem]">
              NOISE
              <br />
              <span className="text-stroke bg-gradient-to-r from-fuchsia-500 via-cyan-400 to-lime-400 bg-clip-text text-transparent">
                MAKER
              </span>
            </h1>

            {/* Tagline with attitude */}
            <div className="mb-8 flex flex-wrap items-center gap-2 text-lg font-bold uppercase tracking-wide md:text-2xl">
              <span className="bg-white px-2 py-1 text-black">GET HEARD.</span>
              <span className="bg-fuchsia-500 px-2 py-1 text-black">GET BOOKED.</span>
              <span className="bg-cyan-400 px-2 py-1 text-black">GET LEGENDARY.</span>
            </div>

            {/* Subtitle - more casual */}
            <p className="mb-12 max-w-xl text-lg text-gray-400 md:text-xl">
              stop wasting hours on promo that doesn&apos;t work.
              <br />
              <span className="text-white">we post to 8 platforms. you make music.</span>
            </p>

            {/* CTA - brutalist style */}
            <Link
              href="/pricing"
              className="group relative inline-block"
            >
              <span className="absolute inset-0 translate-x-2 translate-y-2 bg-fuchsia-500 transition-transform group-hover:translate-x-0 group-hover:translate-y-0" />
              <span className="relative flex items-center gap-3 border-2 border-white bg-black px-8 py-4 text-lg font-black uppercase tracking-wider text-white transition-transform group-hover:translate-x-2 group-hover:translate-y-2">
                Choose Your Path
                <span className="text-2xl">→</span>
              </span>
            </Link>
          </div>
        </section>

        {/* ========== FEATURE STRIP - Scrolling marquee style ========== */}
        <section className="overflow-hidden border-y-4 border-white bg-lime-400 py-4">
          <div className="flex animate-marquee whitespace-nowrap">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex shrink-0 items-center gap-8 px-4">
                {[
                  'NO FAKE STREAMS',
                  'SOCIAL AMPLIFICATION',
                  'LIVE STATS',
                  'FREE HD ARTWORK',
                  '42-DAY PROMO CYCLE',
                ].map((feature, index) => (
                  <span
                    key={index}
                    className="flex items-center gap-2 text-lg font-black uppercase text-black"
                  >
                    <span>★</span>
                    {feature}
                    <span>★</span>
                  </span>
                ))}
              </div>
            ))}
          </div>
        </section>

        {/* ========== PROBLEM / SOLUTION - Stacked brutalist ========== */}
        <section className="px-6 py-16 md:py-24">
          <div className="mx-auto max-w-4xl">

            {/* THE STRUGGLE */}
            <div className="mb-8 border-4 border-white bg-black p-6 md:p-10">
              <div className="-mt-10 mb-6 inline-block bg-red-500 px-4 py-2 md:-mt-14">
                <h2 className="text-2xl font-black uppercase text-black md:text-4xl">
                  THE STRUGGLE
                </h2>
              </div>

              <p className="mb-6 text-lg text-gray-400">
                your music slaps but self-promo? not it.
              </p>

              <div className="grid gap-3 md:grid-cols-2">
                {[
                  'Creating Content = Time Sink',
                  'Inconsistent Reach',
                  'Limited Audience',
                  'Algorithm Doesn\'t Know You',
                  'Marketing > Making Music (wrong)',
                ].map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 border border-gray-800 bg-gray-900 p-3"
                  >
                    <span className="text-red-500">✕</span>
                    <span className="text-sm font-bold uppercase text-white md:text-base">
                      {item}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* THE SOLUTION */}
            <div className="border-4 border-fuchsia-500 bg-black p-6 md:p-10">
              <div className="-mt-10 mb-6 inline-block bg-fuchsia-500 px-4 py-2 md:-mt-14">
                <h2 className="text-2xl font-black uppercase text-black md:text-4xl">
                  THE SOLUTION
                </h2>
              </div>

              <p className="mb-2 text-2xl font-black uppercase text-white md:text-3xl">
                Enter NOISEMAKER
              </p>
              <p className="mb-6 text-lg text-gray-400">
                your promo weapon. 8 platforms. zero effort.
              </p>

              <div className="grid gap-3 md:grid-cols-2">
                {[
                  'Optimized Posting',
                  'Strategic Scheduling',
                  'Maximum Reach',
                  'Algorithm Triggering',
                ].map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 border border-fuchsia-500/30 bg-fuchsia-500/10 p-3"
                  >
                    <span className="text-lime-400">✓</span>
                    <span className="text-sm font-bold uppercase text-white md:text-base">
                      {item}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-8 border-t border-gray-800 pt-6">
                <p className="text-center text-xl font-black uppercase text-fuchsia-400 md:text-2xl">
                  &ldquo;you focus on music. we handle marketing.&rdquo;
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ========== FOOTER CTA ========== */}
        <section className="bg-white px-6 py-16 text-center md:py-24">
          <h2 className="mb-4 text-3xl font-black uppercase text-black md:text-5xl">
            Ready to blow up?
          </h2>
          <p className="mb-8 text-lg text-gray-600">
            (your career, not your laptop)
          </p>
          <Link
            href="/pricing"
            className="group relative inline-block"
          >
            <span className="absolute inset-0 translate-x-2 translate-y-2 bg-black transition-transform group-hover:translate-x-0 group-hover:translate-y-0" />
            <span className="relative flex items-center gap-3 border-4 border-black bg-fuchsia-500 px-10 py-5 text-xl font-black uppercase tracking-wider text-black transition-transform group-hover:translate-x-2 group-hover:translate-y-2">
              Pick Your Plan
              <span className="text-3xl">→</span>
            </span>
          </Link>
        </section>

        {/* ========== FOOTER ========== */}
        <footer className="border-t-4 border-white bg-black px-6 py-6 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            © 2025 NOiSEMaKER by DooWopp
          </p>
        </footer>
      </div>

      {/* Marquee animation */}
      <style jsx>{`
        @keyframes marquee {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-33.333%);
          }
        }
        .animate-marquee {
          animation: marquee 20s linear infinite;
        }
      `}</style>
    </main>
  );
}
