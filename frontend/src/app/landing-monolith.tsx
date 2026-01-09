'use client';

import Image from 'next/image';
import Link from 'next/link';

/**
 * MONOLITH Design - Bold, Commanding, Unapologetic
 *
 * Colors: Black, White, Red (#EF4444) only
 * Typography: Bebas Neue (massive) + Inter
 * Vibe: Underground poster meets tech giant
 */

const platforms = [
  { name: 'Instagram', abbr: 'IG' },
  { name: 'YouTube', abbr: 'YT' },
  { name: 'TikTok', abbr: 'TT' },
  { name: 'X', abbr: 'X' },
  { name: 'Facebook', abbr: 'FB' },
  { name: 'Discord', abbr: 'DC' },
  { name: 'Reddit', abbr: 'RD' },
  { name: 'Threads', abbr: 'TH' },
];

export default function LandingMonolith() {
  return (
    <main className="min-h-screen w-full bg-black text-white">

      {/* ========== HEADER ========== */}
      <header className="flex items-center justify-between px-8 py-6 md:px-16 md:py-8">
        <Link href="/">
          <Image
            src="/doowopp-logo.png"
            alt="DooWopp"
            width={0}
            height={0}
            className="h-14 w-auto brightness-0 invert"
          />
        </Link>
        <Link
          href="/auth/signin"
          className="text-sm font-semibold uppercase tracking-wider text-red-500 transition-colors hover:text-red-400"
        >
          Sign In
        </Link>
      </header>

      {/* ========== HERO ========== */}
      <section className="flex min-h-[90vh] flex-col justify-center px-8 md:px-16">
        {/* Brand */}
        <div className="mb-8">
          <p className="mb-2 text-sm font-semibold uppercase tracking-[0.5em] text-white/60">
            N O I S E M A K E R
          </p>
          <div className="h-0.5 w-48 bg-red-500" />
        </div>

        {/* Logo */}
        <div className="mb-12">
          <Image
            src="/n-logo.png"
            alt="NOiSEMaKER"
            width={180}
            height={180}
            className="h-36 w-36 md:h-44 md:w-44"
          />
        </div>

        {/* Headline - Stacked for impact */}
        <h1 className="mb-8 font-bebas text-6xl uppercase leading-[0.9] tracking-tight md:text-8xl lg:text-[120px]">
          Unleash
          <br />
          Your Music&apos;s
          <br />
          Potential.
        </h1>

        {/* Red rule */}
        <div className="mb-6 h-0.5 w-full max-w-2xl bg-red-500" />

        {/* Subline */}
        <p className="mb-10 max-w-xl text-lg text-neutral-500 md:text-xl">
          The must-have tool for musicians ready to skyrocket growth and stream counts.
        </p>

        {/* CTA */}
        <Link
          href="/pricing"
          className="inline-block bg-red-500 px-10 py-4 text-center text-lg font-semibold uppercase tracking-wider text-white transition-all hover:bg-red-600"
        >
          Get Started
        </Link>

        {/* Scroll indicator */}
        <div className="mt-16 animate-bounce text-center text-neutral-600">
          <span className="text-2xl">↓</span>
        </div>
      </section>

      {/* ========== THE STRUGGLE / SOLUTION - Split ========== */}
      <section className="grid min-h-screen md:grid-cols-2">
        {/* Left - The Struggle */}
        <div className="flex flex-col justify-center bg-neutral-950 px-8 py-16 md:px-16">
          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-neutral-600">
            The
          </p>
          <h2 className="mb-8 font-bebas text-5xl uppercase tracking-tight text-neutral-400 md:text-6xl">
            Struggle
          </h2>
          <p className="mb-8 text-lg text-neutral-500">
            Your music is amazing. But self-promotion? Not your thing.
          </p>
          <ul className="space-y-4 text-neutral-600">
            <li className="flex items-start gap-3">
              <span className="text-neutral-700">×</span>
              <span>Manual posting across platforms</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-neutral-700">×</span>
              <span>Inconsistent reach and engagement</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-neutral-700">×</span>
              <span>Time lost to marketing instead of creating</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-neutral-700">×</span>
              <span>Fighting algorithms you don&apos;t understand</span>
            </li>
          </ul>
        </div>

        {/* Right - The Solution */}
        <div className="flex flex-col justify-center border-l-4 border-red-500 bg-black px-8 py-16 md:px-16">
          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-red-500">
            The
          </p>
          <h2 className="mb-8 font-bebas text-5xl uppercase tracking-tight text-white md:text-6xl">
            Solution
          </h2>
          <p className="mb-8 text-lg text-neutral-300">
            Enter NOiSEMaKER. Your ultimate promotional weapon.
          </p>
          <div className="space-y-2 text-xl font-semibold text-white">
            <p>8 platforms.</p>
            <p>Automated.</p>
            <p>Strategic.</p>
            <p className="text-red-500">Relentless.</p>
          </div>
          <Link
            href="/pricing"
            className="mt-10 inline-flex h-12 w-12 items-center justify-center bg-red-500 text-2xl text-white transition-colors hover:bg-red-600"
          >
            →
          </Link>
        </div>
      </section>

      {/* ========== 8 PLATFORMS ========== */}
      <section className="px-8 py-24 md:px-16">
        <div className="mb-4 font-bebas text-8xl text-red-500 md:text-[144px]">8</div>
        <h2 className="mb-2 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          Platforms
        </h2>
        <div className="mb-12 h-0.5 w-32 bg-white" />
        <p className="mb-16 font-bebas text-3xl uppercase text-neutral-400 md:text-4xl">
          One System.
        </p>

        {/* Platform grid */}
        <div className="mb-12 flex flex-wrap items-center gap-8 md:gap-12">
          {platforms.map((platform) => (
            <div key={platform.abbr} className="text-center">
              <p className="text-lg font-semibold uppercase tracking-wider text-neutral-500">
                {platform.abbr}
              </p>
              <div className="mx-auto mt-2 h-2 w-2 rounded-full bg-white" />
            </div>
          ))}
        </div>

        <p className="max-w-xl text-lg text-neutral-500">
          Your music. Everywhere. No manual posting. No headaches. Just results.
        </p>
      </section>

      {/* ========== THREE PILLARS ========== */}
      <section className="border-t border-neutral-900 px-8 py-24 md:px-16">
        {/* Pillar 1 */}
        <div className="mb-16 border-b border-neutral-900 pb-16">
          <p className="mb-2 font-bebas text-5xl text-red-500">01</p>
          <h3 className="mb-6 font-bebas text-4xl uppercase tracking-tight">No Bots</h3>
          <p className="max-w-2xl text-lg text-neutral-500">
            We don&apos;t do bots. Spotify finds them. They always find them. We do this right.
            Real growth. Real results. It&apos;s not an overnight fix—just trust the process.
          </p>
        </div>

        {/* Pillar 2 */}
        <div className="mb-16 border-b border-neutral-900 pb-16">
          <p className="mb-2 font-bebas text-5xl text-red-500">02</p>
          <h3 className="mb-6 font-bebas text-4xl uppercase tracking-tight">Algorithm Optimized</h3>
          <p className="max-w-2xl text-lg text-neutral-500">
            Algorithms don&apos;t care if your music is amazing or garbage. We optimize your reach
            by getting you into each platform&apos;s good books. Time and consistency—we have you covered.
          </p>
        </div>

        {/* Pillar 3 */}
        <div>
          <p className="mb-2 font-bebas text-5xl text-red-500">03</p>
          <h3 className="mb-6 font-bebas text-4xl uppercase tracking-tight">Simple Setup</h3>
          <p className="max-w-2xl text-lg text-neutral-500">
            Give us your song IDs. That&apos;s it. We handle everything else—posting, scheduling,
            optimization. Your work is done.
          </p>
        </div>
      </section>

      {/* ========== HOW IT WORKS ========== */}
      <section className="bg-neutral-950 px-8 py-24 md:px-16">
        <h2 className="mb-2 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          How It
        </h2>
        <h2 className="mb-4 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          Works
        </h2>
        <div className="mb-16 h-0.5 w-24 bg-red-500" />

        <div className="mb-12 border border-neutral-800 p-8 md:p-12">
          <div className="grid gap-12 md:grid-cols-3">
            {/* Step 1 */}
            <div>
              <p className="mb-4 font-bebas text-4xl text-red-500">01</p>
              <h3 className="mb-4 font-bebas text-2xl uppercase">Connect Platforms</h3>
              <p className="text-neutral-500">
                Link 8 platforms. One click.
              </p>
            </div>
            {/* Step 2 */}
            <div>
              <p className="mb-4 font-bebas text-4xl text-red-500">02</p>
              <h3 className="mb-4 font-bebas text-2xl uppercase">Add Your Songs</h3>
              <p className="text-neutral-500">
                Your Spotify IDs. We pull the rest.
              </p>
            </div>
            {/* Step 3 */}
            <div>
              <p className="mb-4 font-bebas text-4xl text-red-500">03</p>
              <h3 className="mb-4 font-bebas text-2xl uppercase">Watch It Grow</h3>
              <p className="text-neutral-500">
                We post strategically. You relax.
              </p>
            </div>
          </div>
        </div>

        <p className="font-bebas text-2xl uppercase text-white">
          No complicated setup. No hidden fees.
        </p>
      </section>

      {/* ========== 42-DAY CYCLE ========== */}
      <section className="px-8 py-24 md:px-16">
        <h2 className="mb-2 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          The 42-Day
        </h2>
        <h2 className="mb-4 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          Cycle
        </h2>
        <div className="mb-8 h-0.5 w-32 bg-red-500" />
        <p className="mb-12 text-lg text-neutral-500">
          A strategic timeline designed to maximize impact.
        </p>

        {/* Progress bar */}
        <div className="mb-8 h-3 w-full max-w-4xl overflow-hidden bg-neutral-900">
          <div className="flex h-full">
            <div className="h-full w-[20%] bg-red-500" />
            <div className="h-full w-[50%] bg-red-600" />
            <div className="h-full w-[30%] bg-red-700" />
          </div>
        </div>

        {/* Phase labels */}
        <div className="mb-16 grid max-w-4xl gap-8 md:grid-cols-3">
          <div>
            <p className="mb-1 text-sm text-neutral-600">20%</p>
            <h3 className="mb-2 font-bebas text-2xl uppercase">Upcoming</h3>
            <p className="text-sm text-neutral-600">Days 1-14</p>
            <p className="mt-2 text-neutral-500">Building anticipation. Teaser content.</p>
          </div>
          <div>
            <p className="mb-1 text-sm text-neutral-600">50%</p>
            <h3 className="mb-2 font-bebas text-2xl uppercase">Live</h3>
            <p className="text-sm text-neutral-600">Days 15-28</p>
            <p className="mt-2 text-neutral-500">Peak promotion. Maximum visibility.</p>
          </div>
          <div>
            <p className="mb-1 text-sm text-neutral-600">30%</p>
            <h3 className="mb-2 font-bebas text-2xl uppercase">Twilight</h3>
            <p className="text-sm text-neutral-600">Days 29-42</p>
            <p className="mt-2 text-neutral-500">Sustained engagement. Momentum.</p>
          </div>
        </div>

        {/* Fire Mode */}
        <div className="max-w-2xl border-2 border-red-500 p-6 md:p-8">
          <h3 className="mb-4 font-bebas text-3xl uppercase text-red-500">
            🔥 Fire Mode
          </h3>
          <p className="text-neutral-300">
            When your track goes viral, we shift 70% of all posts to that song.
            Ride the wave when it matters.
          </p>
        </div>
      </section>

      {/* ========== STATS ========== */}
      <section className="bg-neutral-950 px-8 py-24 md:px-16">
        <div className="flex flex-wrap items-end justify-center gap-16 text-center md:gap-24">
          <div>
            <p className="font-bebas text-7xl text-white md:text-[144px]">8</p>
            <p className="text-sm font-semibold uppercase tracking-widest text-neutral-500">
              Platforms
            </p>
          </div>
          <div>
            <p className="font-bebas text-7xl text-white md:text-[144px]">42</p>
            <p className="text-sm font-semibold uppercase tracking-widest text-neutral-500">
              Day Cycle
            </p>
          </div>
          <div>
            <p className="font-bebas text-7xl text-white md:text-[144px]">3</p>
            <p className="text-sm font-semibold uppercase tracking-widest text-neutral-500">
              Months
            </p>
          </div>
        </div>
      </section>

      {/* ========== FINAL CTA ========== */}
      <section className="px-8 py-24 md:px-16">
        <div className="mb-8 h-0.5 w-full bg-red-500" />

        <h2 className="mb-2 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          Ready To
        </h2>
        <h2 className="mb-2 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          Grow Your
        </h2>
        <h2 className="mb-12 font-bebas text-5xl uppercase tracking-tight md:text-7xl">
          Fanbase?
        </h2>

        <Link
          href="/pricing"
          className="mb-12 inline-block bg-red-500 px-12 py-5 text-xl font-semibold uppercase tracking-wider text-white transition-all hover:bg-red-600"
        >
          Get Started Now
        </Link>

        <div className="mb-8 flex flex-wrap gap-8 text-sm text-neutral-500">
          <span className="flex items-center gap-2">
            <span className="text-neutral-600">✓</span> No Bots
          </span>
          <span className="flex items-center gap-2">
            <span className="text-neutral-600">✓</span> Cancel Anytime
          </span>
          <span className="flex items-center gap-2">
            <span className="text-neutral-600">✓</span> 5-Min Setup
          </span>
        </div>

        <div className="h-0.5 w-full bg-red-500" />
      </section>

      {/* ========== FOOTER ========== */}
      <footer className="border-t border-neutral-900 px-8 py-12 text-center md:px-16">
        <p className="mb-2 font-bebas text-2xl uppercase tracking-wider">NOiSEMaKER</p>
        <p className="mb-6 text-sm text-neutral-600">by DooWopp © 2025</p>
        <div className="flex justify-center gap-6 text-xs uppercase tracking-wider text-neutral-600">
          <a href="#" className="hover:text-white">Terms</a>
          <a href="#" className="hover:text-white">Privacy</a>
          <a href="#" className="hover:text-white">Contact</a>
        </div>
      </footer>
    </main>
  );
}
