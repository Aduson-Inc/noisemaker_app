// NoiseMaker - API Client
// Phase 2 Implementation
// Handles all backend communication

import axios from 'axios';
import type {
  AuthResponse,
  MilestoneCheckResponse,
  OAuthResponse,
  OAuthCallbackResponse,
  PaymentCheckoutResponse,
  PaymentConfirmResponse,
  PlatformStatusResponse,
  ValidateArtistResponse,
  ValidateTrackResponse
} from '@/types';

// CRITICAL: Must always point to FastAPI backend
// Production: https://api.noisemaker.doowopp.com
// Development: http://localhost:8000 (set NEXT_PUBLIC_API_URL in .env.local)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.noisemaker.doowopp.com';

if (!process.env.NEXT_PUBLIC_API_URL) {
  console.warn('⚠️ NEXT_PUBLIC_API_URL not set - using production: https://api.noisemaker.doowopp.com');
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ============================================================================
// AUTH API
// ============================================================================

// Spotify data interface for signup
interface SpotifyArtistData {
  spotify_artist_id?: string;
  spotify_artist_name?: string;
  spotify_artist_image_url?: string;
  spotify_genres?: string[];
  spotify_followers?: number;
  spotify_external_url?: string;
}

export const authAPI = {
  /**
   * Sign up a new user with all Spotify artist data
   */
  signUp: async (
    email: string,
    password: string,
    name: string,
    tier: 'pending' | 'talent' | 'star' | 'legend',
    spotifyData?: SpotifyArtistData
  ) => {
    return apiClient.post<AuthResponse>('/api/auth/signup', {
      email,
      password,
      name,
      tier,
      ...spotifyData  // Spread all Spotify fields
    });
  },

  /**
   * Sign in an existing user
   */
  signIn: async (email: string, password: string) => {
    return apiClient.post<AuthResponse>('/api/auth/signin', {
      email,
      password
    });
  },

  /**
   * Check if user has pending milestones
   */
  checkMilestones: async (userId: string) => {
    return apiClient.get<MilestoneCheckResponse>(`/api/user/${userId}/milestones`);
  },

  /**
   * Mark a milestone as claimed
   */
  claimMilestone: async (userId: string, milestoneId: string) => {
    return apiClient.post(`/api/user/${userId}/milestones/${milestoneId}/claim`);
  }
};

// ============================================================================
// SPOTIFY API (Artist Validation)
// ============================================================================

export const spotifyAPI = {
  /**
   * Validate a Spotify artist URL and return artist info.
   * PUBLIC endpoint - no auth required (used on pricing page before signup).
   */
  validateArtist: async (url: string) => {
    return apiClient.post<ValidateArtistResponse>('/api/songs/validate-artist', { url });
  }
};

// ============================================================================
// SONGS API
// ============================================================================

export const songsAPI = {
  /**
   * Validate a Spotify track URL and check artist ownership
   * Returns track info if valid and owned by the user
   */
  validateTrack: async (spotifyUrl: string) => {
    return apiClient.post<ValidateTrackResponse>('/api/songs/validate-track', {
      spotify_url: spotifyUrl
    });
  },

  /**
   * Add song from Spotify URL with initial days in promotion
   */
  addSongFromUrl: async (
    userId: string,
    spotifyUrl: string,
    initialDays: number,
    releaseDate?: string
  ) => {
    return apiClient.post('/api/songs/add-from-url', {
      user_id: userId,
      spotify_url: spotifyUrl,
      initial_days: initialDays,
      release_date: releaseDate
    });
  },

  /**
   * Get user's songs
   */
  getUserSongs: async (userId: string) => {
    return apiClient.get(`/api/user/${userId}/songs`);
  }
};

// ============================================================================
// PLATFORM OAUTH API (8 platforms)
// ============================================================================

export const platformAPI = {
  /**
   * Get platform OAuth URL
   */
  getAuthUrl: async (platform: string, userId: string) => {
    return apiClient.get<OAuthResponse>(`/api/oauth/${platform}/connect?user_id=${userId}`);
  },

  /**
   * Handle platform OAuth callback
   */
  handleCallback: async (platform: string, code: string, userId: string) => {
    return apiClient.post<OAuthCallbackResponse>(`/api/oauth/${platform}/callback`, {
      code,
      user_id: userId
    });
  },

  /**
   * Save user's selected platforms
   */
  savePlatforms: async (userId: string, platforms: string[]) => {
    return apiClient.post(`/api/user/${userId}/platforms`, {
      platforms
    });
  },

  /**
   * Get user's platform connections and selection status
   */
  getConnectionsStatus: async (userId: string) => {
    return apiClient.get<PlatformStatusResponse>(`/api/user/${userId}/platforms/status`);
  }
};

// ============================================================================
// PAYMENT API
// ============================================================================

export const paymentAPI = {
  /**
   * Create Stripe checkout session
   */
  createCheckoutSession: async (userId: string, tier: 'talent' | 'star' | 'legend') => {
    return apiClient.post<PaymentCheckoutResponse>('/api/payment/create-checkout', {
      user_id: userId,
      tier
    });
  },

  /**
   * Confirm payment completion
   */
  confirmPayment: async (sessionId: string) => {
    return apiClient.post<PaymentConfirmResponse>('/api/payment/confirm', {
      session_id: sessionId
    });
  }
};

// ============================================================================
// FRANK'S GARAGE API (AI-Generated Art Marketplace)
// ============================================================================

export const frankGarageAPI = {
  /**
   * Get Frank Art with filtering
   * Filters: all, new (7 days), popular (5+ downloads), exclusive (0 downloads)
   */
  getArtwork: async (filter: 'all' | 'new' | 'popular' | 'exclusive' = 'all', userId?: string) => {
    const params = new URLSearchParams({ filter });
    if (userId) params.append('user_id', userId);
    return apiClient.get(`/api/frank-art/artwork?${params.toString()}`);
  },

  /**
   * Get user's art tokens
   * Returns: art_tokens, tokens_from_songs, max_song_tokens (12)
   */
  getTokens: async (userId: string) => {
    return apiClient.get(`/api/frank-art/tokens?user_id=${userId}`);
  },

  /**
   * Place 5-minute hold on artwork for preview/purchase
   */
  placeHold: async (userId: string, artworkId: string) => {
    return apiClient.post('/api/frank-art/hold', {
      user_id: userId,
      artwork_id: artworkId
    });
  },

  /**
   * Release hold on artwork
   */
  releaseHold: async (artworkId: string) => {
    return apiClient.post('/api/frank-art/release-hold', {
      artwork_id: artworkId
    });
  },

  /**
   * FREE download using 1 art token
   * Art stays in pool (others can still get it)
   */
  downloadFree: async (userId: string, artworkId: string) => {
    return apiClient.post('/api/frank-art/download', {
      user_id: userId,
      artwork_id: artworkId
    });
  },

  /**
   * Create Stripe payment intent for purchase
   * NO tokens used - costs money only
   */
  createPaymentIntent: async (
    userId: string,
    artworkIds: string[],
    purchaseType: 'single' | 'bundle_5' | 'bundle_15'
  ) => {
    return apiClient.post('/api/frank-art/create-payment-intent', {
      user_id: userId,
      artwork_ids: artworkIds,
      purchase_type: purchaseType
    });
  },

  /**
   * Confirm purchase after Stripe payment
   * Art removed from pool immediately
   */
  confirmPurchase: async (paymentIntentId: string) => {
    return apiClient.post('/api/frank-art/confirm-purchase', {
      payment_intent_id: paymentIntentId
    });
  },

  /**
   * Get user's downloaded/purchased artwork collection
   */
  getMyCollection: async (userId: string) => {
    return apiClient.get(`/api/frank-art/my-collection?user_id=${userId}`);
  },

  /**
   * Get marketplace analytics (admin)
   */
  getAnalytics: async () => {
    return apiClient.get('/api/frank-art/analytics');
  }
};

// Backwards compatibility alias
export const marketplaceAPI = frankGarageAPI;

// ============================================================================
// DASHBOARD API
// ============================================================================

export const dashboardAPI = {
  /**
   * Get user's songs
   */
  getSongs: async (userId: string) => {
    return apiClient.get(`/api/user/${userId}/songs`);
  },

  /**
   * Get upcoming post for a song
   */
  getUpcomingPost: async (userId: string, songId: string) => {
    return apiClient.get(`/api/user/${userId}/songs/${songId}/upcoming-post`);
  },

  /**
   * Update post caption
   */
  updateCaption: async (postId: string, caption: string) => {
    return apiClient.patch(`/api/posts/${postId}/caption`, {
      caption
    });
  },

  /**
   * Approve a post
   */
  approvePost: async (postId: string) => {
    return apiClient.post(`/api/posts/${postId}/approve`);
  },

  /**
   * Reject a post
   */
  rejectPost: async (postId: string) => {
    return apiClient.post(`/api/posts/${postId}/reject`);
  },

  /**
   * Get user stats
   */
  getUserStats: async (userId: string) => {
    return apiClient.get(`/api/user/${userId}/stats`);
  }
};

export default apiClient;
