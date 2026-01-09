'use client';

import Image from 'next/image';
import Link from 'next/link';

const platforms = [
  { name: 'Instagram', abbr: 'IG' },
  { name: 'YouTube', abbr: 'YT' },
  { name: 'TikTok', abbr: 'TT' },
  { name: 'X/Twitter', abbr: 'X' },
  { name: 'Facebook', abbr: 'FB' },
  { name: 'Discord', abbr: 'DC' },
  { name: 'Reddit', abbr: 'RD' },
  { name: 'Threads', abbr: 'TH' },
];

export default function LandingNoirLuxe() {
  return (
    <main className="min-h-screen w-full bg-black text-white">
      {/* HEADER */}
      <header className="fixed top-0 left-0 right-0 z-50 px-12 py-6 flex items-center justify-between bg-black/80 backdrop-blur-sm">
        <div className="h-12 relative">
          <Image
            src="/images/doowopp-logo-white.png"
            alt="DooWopp"
            width={160}
            height={48}
            className="h-12 w-auto object-contain"
            priority
          />
        </div>
        <Link
          href="/sign-in"
          className="text-[#D4AF37] hover:text-[#E8D5A3] transition-colors font-medium"
        >
          Sign In
        </Link>
      </header>

      {/* HERO SECTION */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-12 relative">
        {/* Logo */}
        <div className="mb-12">
          <Image
            src="/images/noisemaker-logo.png"
            alt="NOiSEMaKER"
            width={450}
            height={180}
            className="h-44 w-auto object-contain"
            priority
          />
        </div>

        <h1 className="font-cormorant text-5xl md:text-7xl font-semibold text-center text-white mb-6 tracking-tight">
          Unleash Your Music&apos;s<br />Potential
        </h1>

        {/* Decorative Divider */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-px bg-[#D4AF37]" />
          <span className="text-[#D4AF37]">&#9670;</span>
          <div className="w-16 h-px bg-[#D4AF37]" />
        </div>

        <p className="text-xl text-[#A3A3A3] text-center max-w-xl mb-10 font-light">
          The intelligent promotion system for artists ready to be heard. Finally.
        </p>

        <Link
          href="/pricing"
          className="px-10 py-4 bg-[#D4AF37] text-black font-semibold text-lg hover:bg-[#E8D5A3] transition-all shadow-lg shadow-[#D4AF37]/20"
        >
          Begin Your Journey
        </Link>

        {/* Scroll Indicator */}
        <div className="absolute bottom-12 flex flex-col items-center gap-2 text-[#525252] animate-pulse">
          <span className="text-sm tracking-wider">Scroll to explore</span>
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* THE REALITY - Problem/Solution */}
      <section className="py-24 px-6 md:px-12">
        <p className="text-center text-[#D4AF37] text-sm tracking-[0.3em] mb-16 font-medium">
          THE REALITY
        </p>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Without Us */}
          <div className="p-12 bg-[#0D0D0D] border border-[#262626]">
            <h3 className="text-[#525252] text-sm tracking-widest mb-8">WITHOUT US</h3>
            <ul className="space-y-4 text-[#6B7280]">
              <li>Hours lost to manual posting</li>
              <li>Inconsistent online presence</li>
              <li>Limited platform reach</li>
              <li>Marketing over music-making</li>
            </ul>
          </div>

          {/* With Us */}
          <div className="p-12 bg-[#0D0D0D] border-l-2 border-[#D4AF37]">
            <h3 className="text-[#D4AF37] text-sm tracking-widest mb-8">WITH US</h3>
            <ul className="space-y-4 text-[#F5F5F4]">
              <li>Post once, reach everywhere</li>
              <li>42-day strategic campaign cycle</li>
              <li>8 platforms, fully automated</li>
              <li>You create. We promote.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* PLATFORMS */}
      <section className="py-24 px-6 md:px-12">
        <p className="text-center text-[#D4AF37] text-sm tracking-[0.3em] mb-4 font-medium">
          EIGHT PLATFORMS
        </p>
        <h2 className="font-cormorant text-4xl md:text-5xl font-semibold text-center text-white mb-16">
          One System
        </h2>

        <div className="flex flex-wrap justify-center gap-6 max-w-3xl mx-auto mb-12">
          {platforms.map((platform) => (
            <div
              key={platform.abbr}
              className="w-14 h-14 flex items-center justify-center rounded-full border border-[#262626] text-[#A3A3A3] hover:border-[#D4AF37] hover:text-[#D4AF37] transition-all cursor-default"
            >
              <span className="text-sm font-medium">{platform.abbr}</span>
            </div>
          ))}
        </div>

        <p className="text-center text-[#A3A3A3] max-w-lg mx-auto leading-relaxed">
          Your music, automatically promoted across every platform that matters. No manual posting. No headaches. Just results.
        </p>
      </section>

      {/* PROMISES - Three Pillars */}
      <section className="py-24 px-6 md:px-12 bg-[#0D0D0D]">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            { title: 'No Fake Numbers', desc: 'We don\'t do bots. Spotify finds them. Always. We do this right.' },
            { title: 'Algorithm Intelligence', desc: 'We optimize for each platform\'s preferences.' },
            { title: 'Simple Setup', desc: 'Give us your song IDs. That\'s it. We handle everything.' }
          ].map((pillar) => (
            <div key={pillar.title} className="p-8 border-t-2 border-[#D4AF37] hover:-translate-y-1 transition-transform">
              <h3 className="font-cormorant text-2xl text-white mb-4">{pillar.title}</h3>
              <p className="text-[#A3A3A3] leading-relaxed">{pillar.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-24 px-6 md:px-12">
        <p className="text-center text-[#D4AF37] text-sm tracking-[0.3em] mb-4 font-medium">
          HOW IT WORKS
        </p>

        <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto mt-16 relative">
          {/* Connecting Line */}
          <div className="hidden md:block absolute top-8 left-1/6 right-1/6 h-px bg-[#D4AF37] opacity-30" />

          {[
            { num: '01', title: 'Connect', desc: 'Link up to 8 platforms with a single click.' },
            { num: '02', title: 'Add Your Songs', desc: 'Provide your Spotify IDs. We pull the rest.' },
            { num: '03', title: 'Watch It Grow', desc: 'We post strategically. You track growth.' }
          ].map((step) => (
            <div key={step.num} className="text-center">
              <span className="font-cormorant text-6xl text-[#D4AF37] opacity-30">{step.num}</span>
              <div className="w-8 h-px bg-[#D4AF37] mx-auto my-4" />
              <h3 className="font-cormorant text-2xl text-white mb-3">{step.title}</h3>
              <p className="text-[#A3A3A3]">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 42-DAY CYCLE */}
      <section className="py-24 px-6 md:px-12 bg-[#0D0D0D]">
        <p className="text-center text-[#D4AF37] text-sm tracking-[0.3em] mb-4 font-medium">
          THE 42-DAY CYCLE
        </p>
        <p className="text-center text-[#A3A3A3] mb-12 max-w-lg mx-auto">
          A strategic timeline designed to maximize impact
        </p>

        {/* Progress Bar */}
        <div className="max-w-3xl mx-auto mb-12">
          <div className="flex h-3 rounded-full overflow-hidden bg-[#1A1A1A]">
            <div className="w-[20%] bg-gradient-to-r from-[#D4AF37] to-[#E8D5A3]" />
            <div className="w-[50%] bg-[#D4AF37]" />
            <div className="w-[30%] bg-gradient-to-r from-[#D4AF37] to-[#525252]" />
          </div>
          <div className="flex justify-between mt-2 text-xs text-[#525252]">
            <span>20%</span>
            <span>50%</span>
            <span>30%</span>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {[
            { phase: 'UPCOMING', days: 'Days 1-14', desc: 'Building anticipation. Teaser content.' },
            { phase: 'LIVE', days: 'Days 15-28', desc: 'Peak promotion. Maximum visibility.' },
            { phase: 'TWILIGHT', days: 'Days 29-42', desc: 'Sustained engagement. Momentum.' }
          ].map((p) => (
            <div key={p.phase} className="text-center">
              <h3 className="font-cormorant text-xl text-white mb-1">{p.phase}</h3>
              <p className="text-[#525252] text-sm mb-2">{p.days}</p>
              <p className="text-[#A3A3A3] text-sm">{p.desc}</p>
            </div>
          ))}
        </div>

        {/* Fire Mode */}
        <div className="max-w-xl mx-auto mt-16 p-8 border border-[#D4AF37] bg-[#0D0D0D]" style={{ boxShadow: '0 0 40px rgba(212, 175, 55, 0.1)' }}>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">&#128293;</span>
            <h3 className="font-cormorant text-xl text-white">FIRE MODE</h3>
          </div>
          <p className="text-[#A3A3A3]">
            When your track goes viral, we shift 70% of all posts to ride the wave.
          </p>
        </div>
      </section>

      {/* STATS */}
      <section className="py-24 px-6 md:px-12">
        <div className="flex flex-wrap justify-center gap-16 max-w-4xl mx-auto">
          {[
            { num: '8', label: 'Platforms', sub: 'Comprehensive reach' },
            { num: '42', label: 'Day Cycle', sub: 'Strategic timing' },
            { num: '3', label: 'Months', sub: 'Results guaranteed' }
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <span className="font-cormorant text-8xl md:text-9xl text-[#D4AF37]">{stat.num}</span>
              <p className="text-white text-sm tracking-widest uppercase mt-2">{stat.label}</p>
              <p className="text-[#525252] text-sm mt-1">{stat.sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-24 px-6 md:px-12">
        <div className="max-w-3xl mx-auto text-center">
          {/* Top Line */}
          <div className="w-full h-px bg-[#D4AF37] mb-16" />

          <h2 className="font-cormorant text-4xl md:text-5xl font-semibold text-white mb-8">
            Ready to Let Your Music Speak?
          </h2>

          <Link
            href="/pricing"
            className="inline-block px-12 py-4 bg-[#D4AF37] text-black font-semibold text-lg hover:bg-[#E8D5A3] transition-all shadow-lg shadow-[#D4AF37]/20 mb-8"
          >
            Start Your Journey Today
          </Link>

          <div className="flex justify-center gap-8 text-[#A3A3A3] text-sm">
            <span className="flex items-center gap-2">
              <span className="text-[#86EFAC]">&#10003;</span> No bots
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#86EFAC]">&#10003;</span> Cancel anytime
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#86EFAC]">&#10003;</span> 5-min setup
            </span>
          </div>

          {/* Bottom Line */}
          <div className="w-full h-px bg-[#D4AF37] mt-16" />
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 px-6 border-t border-[#262626]">
        <div className="max-w-4xl mx-auto text-center">
          <p className="font-cormorant text-xl text-white mb-2">NOiSEMaKER</p>
          <p className="text-[#525252] text-sm mb-6">by DooWopp &copy; 2025</p>
          <div className="flex justify-center gap-8 text-[#525252] text-sm">
            <Link href="/terms" className="hover:text-[#D4AF37] transition-colors">Terms</Link>
            <span>&middot;</span>
            <Link href="/privacy" className="hover:text-[#D4AF37] transition-colors">Privacy</Link>
            <span>&middot;</span>
            <Link href="/contact" className="hover:text-[#D4AF37] transition-colors">Contact</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
