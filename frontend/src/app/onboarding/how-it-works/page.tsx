'use client';

import Image from 'next/image';
import Link from 'next/link';

/**
 * HOW IT WORKS #1 - "THE SIMPLE TRUTH"
 *
 * Gen Z Bold Design - Pre-platform selection info page
 * Following page-genz.tsx patterns exactly
 *
 * Flow: Milestone Video → THIS PAGE → Platform Selection
 */

export default function HowItWorksPage() {
  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">

      {/* Noise texture overlay */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Animated background glows */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-1/4 top-1/3 h-[600px] w-[600px] animate-pulse rounded-full bg-fuchsia-500/15 blur-[150px]" />
        <div className="absolute -right-1/4 top-1/2 h-[500px] w-[500px] animate-pulse rounded-full bg-cyan-400/15 blur-[150px]" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-0 left-1/3 h-[400px] w-[400px] animate-pulse rounded-full bg-lime-400/10 blur-[120px]" style={{ animationDelay: '0.5s' }} />
      </div>

      {/* Content Container */}
      <div className="relative z-10">

        {/* ========== HERO SECTION ========== */}
        <section className="flex min-h-screen flex-col items-center justify-center px-6 py-16">

          {/* BIG BOLD N-LOGO */}
          <div className="mb-6 flex flex-col items-center">
            <Image
              src="/n-logo.png"
              alt="NOiSEMaKER"
              width={128}
              height={128}
              className="h-24 w-24 md:h-32 md:w-32"
              priority
            />
            <span className="mt-4 text-xl font-black uppercase tracking-[0.4em] text-white md:text-2xl">
              NOiSEMaKER
            </span>
          </div>

          {/* MASSIVE headline */}
          <h1 className="mb-12 text-center text-[3rem] font-black uppercase leading-[0.9] tracking-tighter text-white md:text-[5rem] lg:text-[7rem]">
            THE SIMPLE
            <br />
            <span className="bg-gradient-to-r from-fuchsia-500 via-cyan-400 to-lime-400 bg-clip-text text-transparent">
              TRUTH
            </span>
          </h1>

          {/* Content card - brutalist style */}
          <div className="mb-12 w-full max-w-2xl border-4 border-white bg-black p-8 md:p-12">
            {/* TODO: Replace this placeholder text with actual content (100-200 words) */}
            {/* You can edit this directly via GitHub app */}
            <p className="mb-6 text-lg leading-relaxed text-gray-300 md:text-xl">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
            </p>
            <p className="mb-6 text-lg leading-relaxed text-gray-300 md:text-xl">
              Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
            <p className="text-lg leading-relaxed text-gray-300 md:text-xl">
              Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.
            </p>
          </div>

          {/* CTA - brutalist style with offset shadow (from landing page) */}
          <Link
            href="/onboarding/platforms"
            className="group relative inline-block"
          >
            <span className="absolute inset-0 translate-x-2 translate-y-2 bg-fuchsia-500 transition-transform group-hover:translate-x-0 group-hover:translate-y-0" />
            <span className="relative flex items-center gap-3 border-4 border-white bg-black px-10 py-5 text-lg font-black uppercase tracking-wider text-white transition-transform group-hover:translate-x-2 group-hover:translate-y-2 md:px-12 md:py-6 md:text-xl">
              LET&apos;S GO
              <span className="text-2xl md:text-3xl">→</span>
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
    </main>
  );
}
