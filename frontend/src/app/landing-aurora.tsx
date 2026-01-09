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

export default function LandingAurora() {
  return (
    <main className="min-h-screen w-full bg-[#0B0E14] text-white relative overflow-hidden">
      {/* Aurora Background Effect */}
      <div
        className="fixed inset-0 pointer-events-none opacity-30"
        style={{
          background: `
            radial-gradient(ellipse at 20% 20%, rgba(13, 148, 136, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(34, 211, 238, 0.08) 0%, transparent 70%)
          `
        }}
      />

      {/* HEADER */}
      <header className="fixed top-0 left-0 right-0 z-50 px-8 py-6 flex items-center justify-between backdrop-blur-md bg-[#0B0E14]/80">
        <div className="h-14 relative">
          <Image
            src="/images/doowopp-logo-white.png"
            alt="DooWopp"
            width={180}
            height={56}
            className="h-14 w-auto object-contain"
            priority
          />
        </div>
        <Link
          href="/sign-in"
          className="px-6 py-2 rounded-lg border border-transparent bg-transparent text-[#94A3B8] hover:text-white transition-all"
          style={{
            borderImage: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8) 1'
          }}
        >
          Sign In
        </Link>
      </header>

      {/* HERO SECTION */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-12 relative">
        {/* Logo Container with Glass Effect */}
        <div
          className="p-8 rounded-2xl mb-8 relative"
          style={{
            background: 'rgba(18, 22, 31, 0.8)',
            backdropFilter: 'blur(12px)',
            border: '1px solid transparent',
            borderImage: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8) 1',
            boxShadow: '0 0 60px rgba(34, 211, 238, 0.15)'
          }}
        >
          <Image
            src="/images/noisemaker-logo.png"
            alt="NOiSEMaKER"
            width={400}
            height={160}
            className="h-40 w-auto object-contain"
            priority
          />
        </div>

        <h1 className="font-space text-5xl md:text-6xl font-bold text-center text-[#F8FAFC] mb-6 tracking-tight">
          UNLEASH YOUR MUSIC&apos;S POTENTIAL
        </h1>

        <p className="text-xl text-[#94A3B8] text-center max-w-2xl mb-10">
          The must-have tool for musicians ready to skyrocket growth and stream counts.
        </p>

        <Link
          href="/pricing"
          className="px-10 py-4 bg-[#FB7185] text-white font-semibold text-lg rounded-lg hover:bg-[#F43F5E] transition-all shadow-lg shadow-[#FB7185]/25"
        >
          Get Started
        </Link>

        {/* Waveform Animation */}
        <div className="flex items-end justify-center gap-1 mt-16 h-16">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="w-1 rounded-full"
              style={{
                background: 'linear-gradient(to top, #0D9488, #22D3EE)',
                height: `${20 + Math.random() * 40}px`,
                animation: `wave 1.2s ease-in-out infinite`,
                animationDelay: `${i * 0.1}s`
              }}
            />
          ))}
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 animate-bounce text-[#22D3EE]">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* THE STRUGGLE / SOLUTION */}
      <section className="py-24 px-6 md:px-12">
        {/* Struggle Card */}
        <div className="max-w-3xl mx-auto mb-8 p-8 rounded-xl bg-[#12161F]">
          <h2 className="font-space text-2xl font-bold text-[#F8FAFC] mb-4">THE STRUGGLE</h2>
          <div className="w-12 h-0.5 bg-[#475569] mb-6" />
          <p className="text-[#94A3B8] text-lg mb-6">
            Your music is amazing, but self-promotion? Not your forte.
          </p>
          <ul className="space-y-3 text-[#94A3B8]">
            <li className="flex items-start gap-3">
              <span className="text-[#475569]">-</span>
              Manual posting across platforms
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#475569]">-</span>
              Inconsistent reach and engagement
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#475569]">-</span>
              Time lost to marketing instead of creating
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#475569]">-</span>
              Fighting algorithms you don&apos;t understand
            </li>
          </ul>
        </div>

        {/* Arrow */}
        <div className="text-center my-6">
          <span
            className="font-space text-xl font-bold"
            style={{
              background: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            ENTER NOISEMAKER
          </span>
        </div>

        {/* Solution Card */}
        <div
          className="max-w-3xl mx-auto p-8 rounded-xl bg-[#12161F] relative"
          style={{
            border: '1px solid transparent',
            borderImage: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8) 1',
            boxShadow: '0 0 40px rgba(34, 211, 238, 0.1)'
          }}
        >
          <h2 className="font-space text-2xl font-bold text-[#F8FAFC] mb-4">THE SOLUTION</h2>
          <div
            className="w-12 h-0.5 mb-6"
            style={{ background: 'linear-gradient(90deg, #0D9488, #22D3EE)' }}
          />
          <p className="text-[#F8FAFC] text-lg mb-6">
            Your ultimate promotional weapon that amplifies your reach across 8 major platforms.
          </p>
          <ul className="space-y-3 text-[#94A3B8]">
            <li className="flex items-start gap-3">
              <span className="text-[#0D9488]">&#10003;</span>
              Automated, strategic posting
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#0D9488]">&#10003;</span>
              Maximum reach, minimum effort
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#0D9488]">&#10003;</span>
              You focus on music. We handle marketing.
            </li>
          </ul>
        </div>
      </section>

      {/* 8 PLATFORMS */}
      <section className="py-24 px-6 md:px-12">
        <h2
          className="font-space text-4xl md:text-5xl font-bold text-center mb-4"
          style={{
            background: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          8 PLATFORMS. ONE SYSTEM.
        </h2>

        <div className="grid grid-cols-4 md:grid-cols-8 gap-4 max-w-4xl mx-auto mt-12">
          {platforms.map((platform) => (
            <div
              key={platform.abbr}
              className="aspect-square flex flex-col items-center justify-center rounded-xl p-4 transition-all hover:scale-105"
              style={{
                background: 'rgba(18, 22, 31, 0.8)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(34, 211, 238, 0.2)'
              }}
            >
              <span className="text-2xl font-bold text-white">{platform.abbr}</span>
              <span className="text-xs text-[#475569] mt-1">{platform.name}</span>
            </div>
          ))}
        </div>

        <p className="text-center text-[#94A3B8] text-lg mt-12 max-w-xl mx-auto">
          Your music, promoted everywhere that matters. Automatically. Intelligently. Relentlessly.
        </p>
      </section>

      {/* THREE PILLARS */}
      <section className="py-24 px-6 md:px-12">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            { icon: '01', title: 'NO BOTS', desc: 'No fake numbers. Spotify finds them. We do this right.' },
            { icon: '02', title: 'ALGORITHM OPTIMIZED', desc: 'We get your music into each platform\'s good books.' },
            { icon: '03', title: 'SIMPLE SETUP', desc: 'Add your song IDs. That\'s it. We do the rest.' }
          ].map((pillar) => (
            <div
              key={pillar.title}
              className="p-8 rounded-xl text-center transition-all hover:-translate-y-1"
              style={{
                background: 'rgba(18, 22, 31, 0.8)',
                backdropFilter: 'blur(8px)',
                boxShadow: '0 0 30px rgba(34, 211, 238, 0.08)'
              }}
            >
              <div
                className="text-5xl font-space font-bold mb-4 opacity-30"
                style={{
                  background: 'linear-gradient(135deg, #0D9488, #22D3EE)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}
              >
                {pillar.icon}
              </div>
              <h3 className="font-space text-xl font-bold text-white mb-4">{pillar.title}</h3>
              <p className="text-[#94A3B8]">{pillar.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-24 px-6 md:px-12">
        <h2 className="font-space text-4xl md:text-5xl font-bold text-center text-white mb-4">
          HOW IT WORKS
        </h2>
        <p className="text-[#94A3B8] text-center mb-16">
          Three simple steps to amplify your music
        </p>

        <div className="flex flex-col md:flex-row items-center justify-center gap-8 max-w-5xl mx-auto">
          {[
            { num: '1', title: 'Connect Platforms', desc: 'Link up to 8 platforms with one click.' },
            { num: '2', title: 'Add Your Songs', desc: 'Provide your Spotify song IDs. We pull metadata automatically.' },
            { num: '3', title: 'Watch It Grow', desc: 'Sit back while we post across all platforms.' }
          ].map((step, i) => (
            <div key={step.num} className="flex flex-col items-center text-center">
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                style={{
                  border: '2px solid',
                  borderImage: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8) 1'
                }}
              >
                <span className="font-space text-2xl font-bold text-white">{step.num}</span>
              </div>
              <h3 className="font-space text-xl font-bold text-white mb-2">{step.title}</h3>
              <p className="text-[#94A3B8] max-w-xs">{step.desc}</p>
              {i < 2 && (
                <div className="hidden md:block absolute" style={{ left: '50%', transform: 'translateX(100px)' }}>
                  <span className="text-[#22D3EE]">→</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 42-DAY CYCLE */}
      <section className="py-24 px-6 md:px-12">
        <h2 className="font-space text-4xl md:text-5xl font-bold text-center text-white mb-4">
          THE 42-DAY CYCLE
        </h2>
        <p className="text-[#94A3B8] text-center mb-12 max-w-xl mx-auto">
          A strategic promotion timeline that maximizes impact
        </p>

        <div
          className="max-w-4xl mx-auto p-8 rounded-xl"
          style={{
            background: 'rgba(18, 22, 31, 0.8)',
            backdropFilter: 'blur(8px)'
          }}
        >
          {/* Progress Bar */}
          <div className="flex h-4 rounded-full overflow-hidden mb-8">
            <div className="w-[20%] bg-[#0D9488]" />
            <div className="w-[50%] bg-[#22D3EE]" />
            <div className="w-[30%] bg-[#38BDF8]" />
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { phase: 'UPCOMING', days: 'Days 1-14', pct: '20%', desc: 'Building anticipation. Teaser content.' },
              { phase: 'LIVE', days: 'Days 15-28', pct: '50%', desc: 'Peak promotion. Maximum visibility.' },
              { phase: 'TWILIGHT', days: 'Days 29-42', pct: '30%', desc: 'Sustained engagement. Momentum.' }
            ].map((p) => (
              <div key={p.phase} className="text-center">
                <h3 className="font-space text-xl font-bold text-white">{p.phase}</h3>
                <p className="text-[#475569] text-sm mb-2">{p.days}</p>
                <p
                  className="font-mono text-2xl font-bold mb-2"
                  style={{
                    background: 'linear-gradient(135deg, #0D9488, #22D3EE)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}
                >
                  {p.pct}
                </p>
                <p className="text-[#94A3B8] text-sm">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Fire Mode */}
        <div
          className="max-w-2xl mx-auto mt-8 p-6 rounded-xl text-center"
          style={{
            background: 'rgba(18, 22, 31, 0.8)',
            border: '2px solid #FB7185',
            boxShadow: '0 0 30px rgba(251, 113, 133, 0.2)'
          }}
        >
          <span className="text-3xl mb-2 block">&#128293;</span>
          <h3 className="font-space text-xl font-bold text-white mb-2">FIRE MODE</h3>
          <p className="text-[#94A3B8]">
            When your track goes viral, we automatically shift 70% of posts to ride the wave.
          </p>
        </div>
      </section>

      {/* STATS */}
      <section className="py-24 px-6 md:px-12">
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {[
            { num: '8', label: 'PLATFORMS' },
            { num: '42', label: 'DAY CYCLE' },
            { num: '3', label: 'MONTHS' }
          ].map((stat) => (
            <div
              key={stat.label}
              className="text-center p-8 rounded-xl"
              style={{
                background: 'rgba(18, 22, 31, 0.8)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(34, 211, 238, 0.2)'
              }}
            >
              <span
                className="font-space text-7xl font-bold"
                style={{
                  background: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}
              >
                {stat.num}
              </span>
              <p className="font-mono text-xs tracking-widest text-[#94A3B8] mt-2">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-24 px-6 md:px-12">
        <div
          className="max-w-3xl mx-auto p-12 rounded-2xl text-center"
          style={{
            background: 'rgba(18, 22, 31, 0.9)',
            backdropFilter: 'blur(12px)',
            border: '1px solid transparent',
            borderImage: 'linear-gradient(135deg, #0D9488, #22D3EE, #38BDF8) 1',
            boxShadow: '0 0 60px rgba(34, 211, 238, 0.15)'
          }}
        >
          <h2 className="font-space text-4xl md:text-5xl font-bold text-white mb-4">
            READY TO GROW<br />YOUR FANBASE?
          </h2>
          <p className="text-[#94A3B8] text-lg mb-8">
            Subscribe now and transform your career.
          </p>
          <Link
            href="/pricing"
            className="inline-block px-12 py-4 bg-[#FB7185] text-white font-semibold text-lg rounded-lg hover:bg-[#F43F5E] transition-all shadow-lg shadow-[#FB7185]/25"
          >
            Start Your Journey
          </Link>
          <div className="flex justify-center gap-8 mt-8 text-[#94A3B8] text-sm">
            <span className="flex items-center gap-2">
              <span className="text-[#0D9488]">&#10003;</span> No Bots
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#0D9488]">&#10003;</span> Cancel Anytime
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#0D9488]">&#10003;</span> 5-Min Setup
            </span>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 px-6 border-t border-[#1A1A1A]">
        <div className="max-w-4xl mx-auto text-center">
          <p className="font-space text-lg text-white mb-2">NOiSEMaKER</p>
          <p className="text-[#475569] text-sm mb-4">by DooWopp &copy; 2025</p>
          <div className="flex justify-center gap-6 text-[#475569] text-sm">
            <Link href="/terms" className="hover:text-white transition-colors">Terms</Link>
            <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
            <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
          </div>
        </div>
      </footer>

      {/* CSS for waveform animation */}
      <style jsx>{`
        @keyframes wave {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(1.5); }
        }
      `}</style>
    </main>
  );
}
