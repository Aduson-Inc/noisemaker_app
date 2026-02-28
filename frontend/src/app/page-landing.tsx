'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';

/* ─── Animation helpers ─── */
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.25, 0.1, 0.25, 1] as const } },
};

const stagger = {
  visible: { transition: { staggerChildren: 0.12 } },
};

function Reveal({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={stagger}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─── Data ─── */
const platforms = [
  { name: 'Instagram', logo: '/instagram_logo.PNG' },
  { name: 'Twitter / X', logo: '/x_logo.PNG' },
  { name: 'Facebook', logo: '/facebook_logo.PNG' },
  { name: 'YouTube', logo: '/youtube_logo.PNG' },
  { name: 'TikTok', logo: '/tiktok_logo.PNG' },
  { name: 'Reddit', logo: '/reddit_logo.PNG' },
  { name: 'Discord', logo: '/discord_logo.PNG' },
  { name: 'Threads', logo: '/threads_logo.PNG' },
];

const steps = [
  {
    num: '01',
    title: 'CONNECT SPOTIFY',
    text: 'Link your artist profile. We pull your tracks, artwork, and metadata automatically.',
  },
  {
    num: '02',
    title: 'CHOOSE YOUR TIER',
    text: 'Talent, Star, or Legend. More platforms, more reach, more noise.',
  },
  {
    num: '03',
    title: 'WE HANDLE THE REST',
    text: '42 days of automated posting across up to 8 platforms. You make music. We make noise.',
  },
];

/* ─── Fonts (inline style refs) ─── */
const title: React.CSSProperties = { fontFamily: "var(--font-display)" };
const body: React.CSSProperties = { fontFamily: "var(--font-body)" };

/* ─── Circuit pattern for HTML sections ─── */
const circuitBg: React.CSSProperties = {
  backgroundImage: `
    linear-gradient(rgba(0,168,255,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,168,255,0.06) 1px, transparent 1px),
    radial-gradient(circle, rgba(0,168,255,0.12) 1px, transparent 1px)
  `,
  backgroundSize: '50px 50px, 50px 50px, 50px 50px',
  backgroundPosition: '0 0, 0 0, 25px 25px',
};

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LANDING PAGE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
export default function LandingPage() {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '25%']);

  return (
    <main className="relative min-h-screen bg-[#010a18] text-white overflow-x-hidden" style={body}>

      {/* ═══════════ NAVIGATION ═══════════ */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 md:px-8 h-14 bg-[#080c18]/92 backdrop-blur-md border-b border-white/[0.08]">
        <Link
          href="/"
          className="text-[1.15rem] tracking-[0.18em] text-white/90 hover:text-white transition-colors"
          style={title}
        >
          NOISEMAKER
        </Link>

        <div className="flex items-center">
          <Link
            href="/pricing"
            className="px-4 py-1.5 text-[12px] font-medium tracking-[0.14em] text-white/75 border border-white/[0.18] hover:bg-white/[0.06] hover:text-white transition-all duration-300"
            style={body}
          >
            PRICING
          </Link>
          <Link
            href="/auth/signin"
            className="px-4 py-1.5 text-[12px] font-medium tracking-[0.14em] text-white/75 border border-white/[0.18] border-l-0 hover:bg-white/[0.06] hover:text-white transition-all duration-300"
            style={body}
          >
            LOG IN
          </Link>
          <Link
            href="/pricing"
            className="px-4 py-1.5 text-[12px] font-medium tracking-[0.14em] text-white bg-white/[0.08] border border-white/[0.18] border-l-0 hover:bg-white/[0.14] transition-all duration-300"
            style={body}
          >
            SIGN UP
          </Link>
        </div>
      </nav>

      {/* ═══════════ HERO — Landing 1 ═══════════ */}
      <section ref={heroRef} className="relative h-screen overflow-hidden">
        {/* Parallax background */}
        <motion.div className="absolute inset-[-10%] will-change-transform" style={{ y: heroY }}>
          <Image
            src="/landing1.webp"
            alt="NOiSEMaKER — automated music promotion platform with glowing soundwave cube"
            fill
            priority
            className="object-cover object-center"
            sizes="100vw"
          />
        </motion.div>

        {/* Top gradient blend into nav */}
        <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-[#080c18] to-transparent z-10" />
        {/* Bottom gradient blend into next section */}
        <div className="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-t from-[#010a18] to-transparent z-10" />

        {/* Scroll indicator */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1.5 z-20">
          <span className="text-[10px] tracking-[0.35em] text-white/30 uppercase" style={body}>Scroll</span>
          <motion.div
            className="w-px h-7 bg-gradient-to-b from-white/40 to-transparent"
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>

        {/* Accessibility */}
        <div className="sr-only">
          <h1>NOISEMAKER - Automated Music Promotion</h1>
          <p>Stop buying fake bot streams and promo that gets your account flagged and blacklisted.</p>
          <p>Stop wasting hours every day instead of doing what you love.</p>
          <p>We post consistent content about your songs. We crack algorithms for you. Zero fake streams.</p>
        </div>
      </section>

      {/* ═══════════ STATS — Landing 2 ═══════════ */}
      <section className="relative h-screen overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="/landing2.webp"
            alt="8 social media platforms, 42-day promo cycle per release, 3 max songs promoted simultaneously — and growing"
            fill
            className="object-cover object-top"
            sizes="100vw"
          />
        </div>

        {/* Top blend */}
        <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-[#010a18] to-transparent z-10" />
        {/* Bottom blend */}
        <div className="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-t from-[#010a18] to-transparent z-10" />

        <div className="sr-only">
          <h2>Any musician&apos;s essential service — triggering promotion across 8 platforms and growing</h2>
          <p>8 social media platforms. 42 day promo cycle per release. 3 max songs promoted simultaneously.</p>
        </div>
      </section>

      {/* ═══════════ STATS BAR (HTML reinforcement) ═══════════ */}
      <div className="relative py-10 border-y border-[#00a8ff]/10 bg-[#010a18]">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#00a8ff]/[0.03] to-transparent" />
        <Reveal className="max-w-3xl mx-auto flex justify-around text-center relative z-10">
          {[
            { val: '8', label: 'Platforms' },
            { val: '42', label: 'Day Cycle' },
            { val: '3', label: 'Songs Max' },
          ].map((s) => (
            <motion.div key={s.label} variants={fadeUp}>
              <div className="text-4xl md:text-5xl font-black text-[#00a8ff]" style={title}>{s.val}</div>
              <div className="mt-1 text-[10px] tracking-[0.25em] text-white/30 uppercase" style={body}>{s.label}</div>
            </motion.div>
          ))}
        </Reveal>
      </div>

      {/* ═══════════ HOW IT WORKS ═══════════ */}
      <section className="relative py-24 md:py-32 px-6 overflow-hidden">
        {/* Circuit pattern */}
        <div className="absolute inset-0" style={circuitBg} />
        {/* Central glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-[#0055cc]/[0.08] blur-[100px]" />

        <Reveal className="max-w-5xl mx-auto relative z-10">
          <motion.div variants={fadeUp} className="text-center mb-16">
            <span className="text-[12px] tracking-[0.4em] text-[#00a8ff]/60 uppercase" style={body}>Simple Process</span>
            <h2 className="mt-3 text-4xl md:text-6xl font-black tracking-tight" style={title}>
              HOW IT WORKS
            </h2>
            <div className="mt-4 mx-auto w-20 h-px bg-gradient-to-r from-transparent via-[#00a8ff]/60 to-transparent" />
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 md:gap-6">
            {steps.map((s) => (
              <motion.div key={s.num} variants={fadeUp} className="group relative">
                <div className="h-full p-8 border border-white/[0.06] bg-white/[0.015] hover:border-[#00a8ff]/30 transition-all duration-500">
                  {/* Step number */}
                  <div className="w-11 h-11 rounded-full border border-[#00a8ff]/25 flex items-center justify-center mb-5">
                    <span className="text-[13px] font-bold text-[#00a8ff]/80" style={body}>{s.num}</span>
                  </div>
                  <h3 className="text-xl tracking-[0.06em] font-bold mb-3" style={title}>{s.title}</h3>
                  <p className="text-sm text-white/40 leading-relaxed" style={body}>{s.text}</p>
                  {/* Bottom glow */}
                  <div className="absolute bottom-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-[#00a8ff]/0 group-hover:via-[#00a8ff]/50 to-transparent transition-all duration-700" />
                </div>
              </motion.div>
            ))}
          </div>

          {/* Connector lines (desktop) */}
          <div className="hidden md:flex absolute top-[calc(50%+20px)] left-[calc(33.33%-12px)] w-[calc(33.33%+24px)] items-center z-0">
            <div className="flex-1 h-px bg-gradient-to-r from-[#00a8ff]/20 to-[#00a8ff]/10" />
          </div>
        </Reveal>
      </section>

      {/* ═══════════ PLATFORMS ═══════════ */}
      <section className="relative py-24 md:py-32 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#010a18] via-[#010e22] to-[#010a18]" />

        <Reveal className="max-w-4xl mx-auto relative z-10">
          <motion.div variants={fadeUp} className="text-center mb-16">
            <span className="text-[12px] tracking-[0.4em] text-[#00a8ff]/60 uppercase" style={body}>Maximum Reach</span>
            <h2 className="mt-3 text-4xl md:text-6xl font-black tracking-tight" style={title}>
              8 PLATFORMS. ZERO EFFORT.
            </h2>
            <div className="mt-4 mx-auto w-20 h-px bg-gradient-to-r from-transparent via-[#00a8ff]/60 to-transparent" />
          </motion.div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 md:gap-8 max-w-2xl mx-auto">
            {platforms.map((p) => (
              <motion.div key={p.name} variants={fadeUp} className="flex flex-col items-center gap-3 group">
                <div className="relative w-16 h-16 md:w-[72px] md:h-[72px] border border-white/[0.08] bg-white/[0.02] flex items-center justify-center group-hover:border-[#00a8ff]/30 group-hover:bg-[#00a8ff]/[0.04] transition-all duration-500">
                  <Image
                    src={p.logo}
                    alt={p.name}
                    width={40}
                    height={40}
                    className="w-9 h-9 md:w-10 md:h-10 object-contain"
                  />
                </div>
                <span
                  className="text-[10px] tracking-[0.18em] text-white/35 group-hover:text-white/60 transition-colors uppercase"
                  style={body}
                >
                  {p.name}
                </span>
              </motion.div>
            ))}
          </div>
        </Reveal>
      </section>

      {/* ═══════════ VALUE PROPS ═══════════ */}
      <section className="relative py-24 md:py-32 px-6 overflow-hidden">
        <div className="absolute inset-0" style={circuitBg} />
        <div className="absolute top-0 left-1/4 w-[400px] h-[400px] rounded-full bg-[#0055cc]/[0.06] blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[300px] h-[300px] rounded-full bg-[#00a8ff]/[0.04] blur-[100px]" />

        <Reveal className="max-w-5xl mx-auto relative z-10">
          <motion.div variants={fadeUp} className="text-center mb-16">
            <span className="text-[12px] tracking-[0.4em] text-[#00a8ff]/60 uppercase" style={body}>Why NOiSEMaKER</span>
            <h2 className="mt-3 text-4xl md:text-6xl font-black tracking-tight" style={title}>
              STOP WASTING TIME
            </h2>
            <div className="mt-4 mx-auto w-20 h-px bg-gradient-to-r from-transparent via-[#00a8ff]/60 to-transparent" />
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                heading: 'NO FAKE STREAMS',
                text: 'We crack algorithms with real content posted to real audiences. Zero bots. Zero flags. Your account stays clean.',
              },
              {
                heading: 'YOU MAKE MUSIC',
                text: 'Stop spending hours every day on promo. Connect once, and our system posts for you across every platform.',
              },
              {
                heading: 'CONSISTENT CONTENT',
                text: 'Algorithm-triggering posts on a 42-day cycle. Your music stays visible without you lifting a finger.',
              },
            ].map((item) => (
              <motion.div key={item.heading} variants={fadeUp} className="group">
                <div className="h-full p-8 border border-white/[0.06] bg-white/[0.015] hover:border-[#00a8ff]/25 transition-all duration-500">
                  <h3 className="text-lg tracking-[0.08em] font-bold text-[#00a8ff] mb-3" style={title}>
                    {item.heading}
                  </h3>
                  <p className="text-sm text-white/40 leading-relaxed" style={body}>{item.text}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </Reveal>
      </section>

      {/* ═══════════ CTA ═══════════ */}
      <section className="relative py-28 md:py-36 px-6 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[280px] rounded-full bg-[#0066ff]/[0.12] blur-[100px]" />

        <Reveal className="max-w-3xl mx-auto text-center relative z-10">
          <motion.h2
            variants={fadeUp}
            className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight leading-[0.95]"
            style={title}
          >
            READY TO MAKE
            <br />
            <span className="text-[#00a8ff]">SOME NOISE?</span>
          </motion.h2>

          <motion.p variants={fadeUp} className="mt-6 text-white/35 text-base md:text-lg" style={body}>
            Join artists who stopped grinding on promo and started making music.
          </motion.p>

          <motion.div variants={fadeUp} className="mt-10">
            <Link
              href="/pricing"
              className="relative inline-flex items-center gap-3 px-10 py-4 text-lg tracking-[0.18em] font-bold text-white border border-[#00a8ff]/60 hover:border-[#00a8ff] hover:bg-[#00a8ff]/[0.08] transition-all duration-400 group"
              style={title}
            >
              GET STARTED
              <span className="text-xl group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
              {/* Outer glow on hover */}
              <span className="absolute -inset-px bg-[#00a8ff]/[0.04] blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            </Link>
          </motion.div>
        </Reveal>
      </section>

      {/* ═══════════ FOOTER ═══════════ */}
      <footer className="relative py-8 px-6 border-t border-white/[0.05]">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-[10px] tracking-[0.3em] text-white/25 uppercase" style={body}>
            &copy; 2026 NOiSEMaKER by ADUSON Inc.
          </span>
          <div className="flex items-center gap-6">
            <Link href="/pricing" className="text-[10px] tracking-[0.2em] text-white/25 hover:text-white/50 transition-colors uppercase" style={body}>
              Pricing
            </Link>
            <Link href="/auth/signin" className="text-[10px] tracking-[0.2em] text-white/25 hover:text-white/50 transition-colors uppercase" style={body}>
              Sign In
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
