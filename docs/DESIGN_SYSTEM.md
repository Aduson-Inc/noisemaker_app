# NOiSEMaKER Design System

## Design: "Gen Z Bold"

**Philosophy:** Anti-corporate, TikTok-native energy. Oversized brutalist typography, high contrast, authentic/raw aesthetic. Designed to stop the scroll and feel intentionally chaotic yet professional.

**Target Audience:** Gen Z musicians (18-25) who value authenticity over polish.

**Chosen:** December 2025

---

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Black | `#000000` | Primary background |
| White | `#FFFFFF` | Primary text, borders, CTA backgrounds |

### Accent Colors
| Name | Hex/Tailwind | Usage |
|------|--------------|-------|
| Fuchsia | `fuchsia-500` (#d946ef) | Primary accent, CTA buttons, Star tier |
| Cyan | `cyan-400` (#22d3ee) | Secondary accent, Talent tier |
| Lime | `lime-400` (#a3e635) | Tertiary accent, badges, Legend tier |
| Red | `red-500` (#ef4444) | Negative indicators, errors |

### Tier-Specific Colors
| Tier | Color | Hex |
|------|-------|-----|
| Talent | Cyan | #22d3ee |
| Star | Fuchsia | #d946ef |
| Legend | Lime | #a3e635 |

### Semantic Colors
```
Success/Positive: lime-400
Error/Negative: red-500
Warning: yellow-500
Primary Action: fuchsia-500
Secondary Action: white
```

---

## Typography

### Font Family
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Font Weights
| Weight | Tailwind Class | Usage |
|--------|----------------|-------|
| 400 | `font-normal` | Body text (rare) |
| 700 | `font-bold` | Emphasis text |
| 900 | `font-black` | Headlines, buttons, key text |

### Font Sizes (Mobile → Desktop)
| Element | Mobile | Desktop | Tailwind |
|---------|--------|---------|----------|
| Main Headline | 4rem | 8-10rem | `text-[4rem] md:text-[8rem] lg:text-[10rem]` |
| Section Headers | 2xl | 4xl | `text-2xl md:text-4xl` |
| Tier Names | 3xl | 5xl | `text-3xl md:text-5xl` |
| Prices | 4xl | 6xl | `text-4xl md:text-6xl` |
| Tagline | lg | 2xl | `text-lg md:text-2xl` |
| Body Text | lg | xl | `text-lg md:text-xl` |
| Labels/Small | sm | base | `text-sm md:text-base` |
| Tiny/Legal | xs | xs | `text-xs` |

### Text Styling
- **All caps:** Used extensively for headlines, buttons, labels
- **Tracking:** `tracking-tighter` for headlines, `tracking-wider`/`tracking-widest` for buttons
- **Line height:** `leading-[0.85]` for tight headline stacking

---

## Key CSS Patterns

### Brutalist Button (Offset Shadow)
```tsx
<button className="group relative inline-block">
  {/* Shadow layer */}
  <span className="absolute inset-0 translate-x-2 translate-y-2 bg-fuchsia-500 transition-transform group-hover:translate-x-0 group-hover:translate-y-0" />
  {/* Button layer */}
  <span className="relative flex items-center gap-3 border-2 border-white bg-black px-8 py-4 text-lg font-black uppercase tracking-wider text-white transition-transform group-hover:translate-x-2 group-hover:translate-y-2">
    Button Text
    <span className="text-2xl">→</span>
  </span>
</button>
```
**Behavior:** On hover, layers swap positions creating a "press" effect.

### Highlight Badges (Inline)
```tsx
<span className="bg-white px-2 py-1 text-black">GET HEARD.</span>
<span className="bg-fuchsia-500 px-2 py-1 text-black">GET BOOKED.</span>
<span className="bg-cyan-400 px-2 py-1 text-black">GET LEGENDARY.</span>
```

### Floating Badge (Rotated)
```tsx
<div className="absolute right-4 top-20 rotate-12 rounded-full border-2 border-lime-400 bg-lime-400 px-4 py-2 text-xs font-black uppercase text-black">
  No fake streams
</div>
```

### Card Sections (Brutalist)
```tsx
<div className="border-4 border-white bg-black p-6 md:p-10">
  <div className="-mt-10 mb-6 inline-block bg-red-500 px-4 py-2 md:-mt-14">
    <h2 className="text-2xl font-black uppercase text-black">HEADER</h2>
  </div>
  {/* Content */}
</div>
```
**Pattern:** Header "tab" uses negative margin to overlap the card border.

### Brutalist Input Fields
```tsx
<input
  type="text"
  placeholder="PLACEHOLDER"
  className="w-full border-2 border-white bg-black px-3 py-2 text-sm font-bold outline-none text-white placeholder-gray-600"
/>
```

### List Items (with Icons)
```tsx
{/* Negative items */}
<div className="flex items-center gap-3 border border-gray-800 bg-gray-900 p-3">
  <span className="text-red-500">✕</span>
  <span className="text-sm font-bold uppercase text-white">{item}</span>
</div>

{/* Positive items */}
<div className="flex items-center gap-3 border border-fuchsia-500/30 bg-fuchsia-500/10 p-3">
  <span className="text-lime-400">✓</span>
  <span className="text-sm font-bold uppercase text-white">{item}</span>
</div>
```

---

## Animations

### Scrolling Marquee
```tsx
<section className="overflow-hidden border-y-4 border-white bg-lime-400 py-4">
  <div className="flex animate-marquee whitespace-nowrap">
    {[...Array(3)].map((_, i) => (
      <div key={i} className="flex shrink-0 items-center gap-8 px-4">
        {features.map((feature, index) => (
          <span key={index} className="text-lg font-black uppercase text-black">
            ★ {feature} ★
          </span>
        ))}
      </div>
    ))}
  </div>
</section>

<style jsx>{`
  @keyframes marquee {
    0% { transform: translateX(0); }
    100% { transform: translateX(-33.333%); }
  }
  .animate-marquee {
    animation: marquee 20s linear infinite;
  }
`}</style>
```

### Noise Texture Overlay
```tsx
<div
  className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
  style={{
    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
  }}
/>
```

### Hover Transitions
```css
transition-transform group-hover:translate-x-2 group-hover:translate-y-2
transition-all hover:bg-white hover:text-black
```

---

## Page Structures

### Landing Page (`/`)

**File:** `frontend/src/app/page-genz.tsx`

**Sections:**
1. Header — Logo + Sign In button
2. Hero — Small logo, MASSIVE headline, tagline badges, subtitle, CTA
3. Feature Strip — Scrolling marquee with stars
4. Problem/Solution — Two stacked brutalist cards
5. Footer CTA — White background section with final CTA
6. Footer — Copyright

---

### Pricing Page (`/pricing`)

**File:** `frontend/src/app/pricing/pricing-v2.tsx`

**Design:** Full-Width Bands (editorial/magazine style)

**Sections:**
1. Header — Logo + Back button
2. Hero — Single word "PRICING" headline
3. Tier Bands — Three full-width horizontal sections (clickable)
4. Expanded Content — Features grid + signup form (appears on click)
5. Bottom CTA — "TAP A PLAN TO GET STARTED" (when nothing selected)
6. Footer — Copyright

**Tier Band Pattern:**
```tsx
<section className={`border-b-4 border-white ${tier.bgColor}`}>
  <button className="flex w-full items-center justify-between">
    {/* Left: Number + Name */}
    <div className="flex items-baseline gap-4">
      <span className="text-6xl font-black text-white/20">01</span>
      <div>
        <h2 className="text-3xl font-black uppercase">{tier.name}</h2>
        <p className="text-sm text-gray-500">{tier.platforms} platforms</p>
      </div>
    </div>
    {/* Right: Price + Arrow */}
    <div className="flex items-center gap-4">
      <span className="text-4xl font-black">${tier.price}</span>
      <div className="h-12 w-12 border-2 border-white text-2xl">↓</div>
    </div>
  </button>
</section>
```

**Star Tier Highlight:**
- Uses `bg-fuchsia-500` background (other tiers use `bg-black`)
- Text colors invert to black
- Creates visual hierarchy for "most popular"

**Form Integration:**
- Form appears inline when tier expanded
- Adapts colors based on selected tier
- Fields: Artist Name, Email, Password
- CTA appears only when all fields valid

---

## Subscription Tiers

| Tier | Price | Platforms | Songs | Color |
|------|-------|-----------|-------|-------|
| Talent | $25/mo | 2 | 3 | Cyan |
| Star | $40/mo | 5 | 3 | Fuchsia |
| Legend | $60/mo | 8 | 3 | Lime |

### Features by Tier

**Talent:** 2 Platforms, 3 Songs/Month, Basic Analytics, 42-Day Cycle

**Star:** 5 Platforms, 3 Songs/Month, Advanced Analytics, 42-Day Cycle, Priority Support

**Legend:** ALL 8 Platforms, 3 Songs/Month, Full Analytics, 42-Day Cycle, Priority Support, Custom Scheduling

---

## Form Validation

| Field | Validation | Error State |
|-------|------------|-------------|
| Artist Name | Not empty | Red border |
| Email | Contains `@` | Red border |
| Password | Min 8 characters | Red text warning |

**Artist Name Warning:**
```tsx
<p className="text-xs text-yellow-500">
  ⚠️ Case sensitive! Must match Spotify exactly.
</p>
```

**Submit Button:** Only appears when ALL fields are valid

---

## File Locations

### Landing Page
- **Primary:** `frontend/src/app/page-genz.tsx`
- **Entry:** `frontend/src/app/page.tsx`
- **Alternatives:** `page-cosmic.tsx`, `page-premium.tsx`

### Pricing Page
- **Primary:** `frontend/src/app/pricing/pricing-v2.tsx`
- **Entry:** `frontend/src/app/pricing/page.tsx`
- **Alternatives:** `pricing-v1.tsx`, `pricing-v3.tsx`

---

## Design Tokens Summary

```typescript
const genZBoldTokens = {
  colors: {
    background: '#000000',
    foreground: '#FFFFFF',
    accent: {
      primary: 'fuchsia-500',
      secondary: 'cyan-400',
      tertiary: 'lime-400',
    },
    semantic: {
      negative: 'red-500',
      positive: 'lime-400',
      warning: 'yellow-500',
    },
    tiers: {
      talent: 'cyan-400',
      star: 'fuchsia-500',
      legend: 'lime-400',
    },
  },
  typography: {
    fontFamily: "'Inter', system-ui, sans-serif",
    weights: { body: 700, heading: 900 },
  },
  borders: {
    width: '2px',
    widthThick: '4px',
  },
  shadows: {
    brutalist: 'translate-x-2 translate-y-2',
  },
};
```

---

## Usage Notes for Future Agents

1. **Brutalist aesthetic** — No rounded corners (except badges), thick borders, offset shadows
2. **Typography is king** — When in doubt, make text bigger and bolder
3. **High contrast only** — Black/white with bright accent pops
4. **All caps for impact** — Headlines, buttons, labels = uppercase
5. **Slightly chaotic** — Rotated badges, offset elements, asymmetry = intentional
6. **Mobile-first** — Start mobile, scale up for desktop
7. **Tier colors are sacred** — Talent=Cyan, Star=Fuchsia, Legend=Lime (always)
8. **Forms are brutalist** — Thick borders, no rounded corners
9. **CTAs appear when valid** — Never show disabled buttons, hide until ready
