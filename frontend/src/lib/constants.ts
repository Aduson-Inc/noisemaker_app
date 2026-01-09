// NoiseMaker - Subscription Tiers and Platform Constants
// Phase 2 Implementation

export const SUBSCRIPTION_TIERS = {
  talent: {
    name: 'Talent',
    monthly_price: 25,
    max_active_songs: 3,
    platforms_limit: 2,
    fire_mode_enabled: true,
    ai_captions_enabled: true,
    milestone_notifications: true,
    description: 'Perfect for emerging artists',
    features: [
      '3 actively promoted songs at a time',
      '42 day promotion cycle per Song',
      'Choose 2 social platforms',
      'Fire Mode enhanced',
      'Personalized Genre Specific captions',
      'Milestone & Stat Tracker'
    ]
  },
  star: {
    name: 'Star',
    monthly_price: 40,
    max_active_songs: 3,
    platforms_limit: 5,
    fire_mode_enabled: true,
    ai_captions_enabled: true,
    milestone_notifications: true,
    description: 'For rising artists gaining traction',
    features: [
      '3 actively promoted songs at a time',
      '42 day promotion cycle per Song',
      'Choose 5 social platforms',
      'Fire Mode enhanced',
      'Personalized Genre Specific captions',
      'Milestone & Stat Tracker'
    ]
  },
  legend: {
    name: 'Legend',
    monthly_price: 60,
    max_active_songs: 3,
    platforms_limit: 8,
    fire_mode_enabled: true,
    ai_captions_enabled: true,
    milestone_notifications: true,
    description: 'Maximum reach for serious artists',
    features: [
      '3 actively promoted songs at a time',
      '42 day promotion cycle per Song',
      '8 social platforms',
      'Fire Mode enhanced',
      'Personalized Genre Specific captions',
      'Milestone & Stat Tracker'
    ]
  }
} as const;

export const PLATFORMS = [
  { id: 'instagram', name: 'Instagram', icon: '/platforms/instagram.svg' },
  { id: 'twitter', name: 'Twitter', icon: '/platforms/twitter.svg' },
  { id: 'facebook', name: 'Facebook', icon: '/platforms/facebook.svg' },
  { id: 'tiktok', name: 'TikTok', icon: '/platforms/tiktok.svg' },
  { id: 'youtube', name: 'YouTube', icon: '/platforms/youtube.svg' },
  { id: 'reddit', name: 'Reddit', icon: '/platforms/reddit.svg' },
  { id: 'discord', name: 'Discord', icon: '/platforms/discord.svg' },
  { id: 'threads', name: 'Threads', icon: '/platforms/threads.svg' },
] as const;

export const MILESTONE_VIDEOS = {
  welcome: {
    male: '/milestones/welcome-industry-male.mp4',
    female: '/milestones/welcome-industry-female.mp4'
  },
  popularity_7: {
    male: '/milestones/popularity-7-male.mp4',
    female: '/milestones/popularity-7-female.mp4'
  },
  popularity_10: {
    male: '/milestones/popularity-10-male.mp4',
    female: '/milestones/popularity-10-female.mp4'
  },
  popularity_15: {
    male: '/milestones/popularity-15-male.mp4',
    female: '/milestones/popularity-15-female.mp4'
  },
  popularity_20: {
    male: '/milestones/popularity-20-male.mp4',
    female: '/milestones/popularity-20-female.mp4'
  },
  popularity_30: {
    male: '/milestones/popularity-30-male.mp4',
    female: '/milestones/popularity-30-female.mp4'
  },
  popularity_40: {
    male: '/milestones/popularity-40-male.mp4',
    female: '/milestones/popularity-40-female.mp4'
  },
  popularity_50: {
    male: '/milestones/popularity-50-male.mp4',
    female: '/milestones/popularity-50-female.mp4'
  },
  loyalty_7: {
    male: '/milestones/loyalty-7-male.mp4',
    female: '/milestones/loyalty-7-female.mp4'
  },
  loyalty_30: {
    male: '/milestones/loyalty-30-male.mp4',
    female: '/milestones/loyalty-30-female.mp4'
  },
  loyalty_90: {
    male: '/milestones/loyalty-90-male.mp4',
    female: '/milestones/loyalty-90-female.mp4'
  },
  loyalty_180: {
    male: '/milestones/loyalty-180-male.mp4',
    female: '/milestones/loyalty-180-female.mp4'
  },
  loyalty_365: {
    male: '/milestones/loyalty-365-male.mp4',
    female: '/milestones/loyalty-365-female.mp4'
  }
} as const;

export type TierKey = keyof typeof SUBSCRIPTION_TIERS;
export type PlatformId = typeof PLATFORMS[number]['id'];
export type Gender = 'male' | 'female';
