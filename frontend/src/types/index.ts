// NoiseMaker - TypeScript Type Definitions
// Phase 2 Implementation

export interface User {
  user_id: string;
  email: string;
  name: string;
  subscription_tier: 'talent' | 'star' | 'legend';
  account_status: 'active' | 'inactive';
  baseline_streams_per_day: number;
  baseline_calculated_at: string;
  baseline_status: 'not_started' | 'collecting' | 'calculated';
  fire_mode_available: boolean;
  spotify_connected: boolean;
  spotify_artist_id: string;
  preferences: {
    platforms_enabled: string[];
    timezone: string;
    ai_captions_enabled: boolean;
  };
  subscription_start: string;
  subscription_expires: string;
}

export interface Song {
  user_id: string;
  song_id: string;
  spotify_track_id: string;
  song: string;
  artist_title: string;
  art_url: string;
  spotify_popularity: number;
  fire_mode: boolean;
  fire_mode_entered_at: string;
  peak_popularity_in_fire_mode: number;
  fire_mode_phase: number | null;
  popularity_history: Array<{
    date: string;
    score: number;
  }>;
  days_in_promotion: number;
  promotion_status: 'active' | 'retired';
}

export interface Milestone {
  user_id: string;
  milestone_id: string;
  milestone_type: string;
  milestone_category: 'popularity' | 'loyalty' | 'instant';
  milestone_value: number;
  queued_at: string;
  expires_at: string;
  milestone_claimed: boolean;
  claimed_at: string | null;
}

export interface PlatformConnection {
  user_id: string;
  platform: string;
  access_token: string;
  refresh_token: string;
  token_expires_at: string;
  connected_at: string;
  platform_user_id: string;
  platform_username: string;
  status: 'active' | 'token_expired' | 'revoked';
}

export interface Post {
  post_id: string;
  user_id: string;
  song_id: string;
  platform: string;
  caption: string;
  image_url: string;
  scheduled_time: string;
  post_status: 'scheduled' | 'posted' | 'failed' | 'rejected';
  approval_status: 'pending' | 'approved' | 'rejected';
  engagement_stats?: {
    likes: number;
    comments: number;
    shares: number;
    reach: number;
  };
}

// Song Slot (dashboard card data from GET /api/user/{userId}/song-slots)
export interface SongSlot {
  song_id: string;
  title: string;
  artist: string;
  album_art_url: string;
  days_in_promotion: number;
  promotion_status: string;
  go_live_date: string | null;
  stage_of_promotion: string;
  has_audio: boolean;
  has_clip: boolean;
  fire_mode: boolean;
}

export interface SongSlotsResponse {
  songs: SongSlot[];
  slots_total: number;
  slots_used: number;
  can_add_song: boolean;
  next_slot_opens_in_days: number | null;
}

// API Response types
export interface AuthResponse {
  user_id: string;
  token: string;
  message?: string;
  // Enhanced fields for smart routing
  name?: string;
  email?: string;
  subscription_tier?: 'pending' | 'talent' | 'star' | 'legend';
  account_status?: 'active' | 'inactive';
  onboarding_status?: string;
  onboarding_complete?: boolean;
  pending_milestone?: string | null;
  milestone_video_url?: string | null;
  redirect_to?: string;
}

export interface MilestoneCheckResponse {
  has_pending: boolean;
  milestone_type: string | null;
  video_url: string | null;
  description?: string;
  artist_name: string;
}

export interface OAuthResponse {
  auth_url: string;
}

export interface OAuthCallbackResponse {
  success: boolean;
  message?: string;
}

export interface PaymentCheckoutResponse {
  checkout_url: string;
}

export interface PaymentConfirmResponse {
  success: boolean;
  message: string;
  token: string;
}

export interface PlatformStatusResponse {
  connections: { [platform: string]: boolean | { connected?: boolean; username?: string; account_type?: string } };
  selected_platforms: string[];
  platform_limit: number;
  subscription_tier: 'pending' | 'talent' | 'star' | 'legend';
}

export interface ValidateArtistResponse {
  success: boolean;
  artist_id: string;
  artist_name: string;
  artist_image_url?: string;
  genres?: string[];
  followers?: number;
  external_url?: string;
}

export interface ValidateTrackResponse {
  success: boolean;
  valid: boolean;
  track_id?: string;
  name?: string;
  artist_name?: string;
  album_art_url?: string;
  preview_url?: string;
  popularity?: number;
  release_date?: string;
  artist_matches_user?: boolean;
  error?: string;
  track_artist?: string;
  your_artist?: string;
}

// Frank's Garage (AI Art Marketplace) types
export interface FrankArtwork {
  artwork_id: string;
  filename: string;
  thumbnail_url: string;
  mobile_url: string;
  original_url: string;
  upload_date: string;
  download_count: number;
  is_purchased: boolean;
  art_style: string;
  artist_style: string;
  color_scheme: string;
  held_by?: string;
  hold_expires_at?: string;
}

export interface FrankArtListResponse {
  success: boolean;
  artwork: FrankArtwork[];
  total: number;
  filter: string;
}

export interface FrankArtTokenResponse {
  success: boolean;
  art_tokens: number;
  tokens_from_songs: number;
  max_song_tokens: number;
}

export interface FrankArtHoldResponse {
  success: boolean;
  artwork_id: string;
  expires_at: string;
  mobile_url: string;
}

export interface FrankArtDownloadResponse {
  success: boolean;
  download_url: string;
  tokens_remaining: number;
}

export interface FrankArtPaymentIntentResponse {
  success: boolean;
  client_secret: string;
  amount: number;
  artwork_count: number;
}

export interface FrankArtPurchaseResponse {
  success: boolean;
  download_urls: string[];
  artworks_purchased: number;
}

export interface FrankArtCollectionItem {
  artwork_id: string;
  thumbnail_url: string;
  type: 'download' | 'purchase';
  acquired_at: string;
}

export interface FrankArtCollectionResponse {
  success: boolean;
  collection: FrankArtCollectionItem[];
  total: number;
}
