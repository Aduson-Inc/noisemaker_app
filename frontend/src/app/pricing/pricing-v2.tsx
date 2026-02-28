'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { authAPI, paymentAPI, spotifyAPI } from '@/lib/api';
import type { ValidateArtistResponse } from '@/types';

/**
 * PRICING DESIGN 2: "Full-Width Bands" + Spotify Artist Validation
 *
 * Gen Z Bold style pricing page
 * - Each tier is a full-width horizontal band
 * - Click to expand and reveal form inline
 * - Bold, editorial magazine feel
 * - High contrast with accent borders
 * - Spotify artist link validation with expandable card
 *
 * PAYMENT FLOW:
 * 1. User pastes Spotify artist URL → auto-validates
 * 2. Artist card expands showing artist image + name
 * 3. User fills form + selects tier
 * 4. POST /api/auth/signup with tier: "pending" + spotify_artist_id
 * 5. POST /api/payment/create-checkout with actual tier
 * 6. Redirect to Stripe checkout_url
 */

interface TierData {
  id: 'talent' | 'star' | 'legend';
  name: string;
  price: number;
  platforms: number;
  songs: number;
  bgColor: string;
  textColor: string;
  accentColor: string;
  features: string[];
}

const tiers: TierData[] = [
  {
    id: 'talent',
    name: 'TALENT',
    price: 25,
    platforms: 2,
    songs: 3,
    bgColor: 'bg-black',
    textColor: 'text-cyan-400',
    accentColor: '#22d3ee',
    features: ['2 Social Platforms', '3 Songs/Month', 'Basic Analytics', '42-Day Cycle'],
  },
  {
    id: 'star',
    name: 'STAR',
    price: 40,
    platforms: 5,
    songs: 3,
    bgColor: 'bg-fuchsia-500',
    textColor: 'text-black',
    accentColor: '#000000',
    features: ['5 Social Platforms', '3 Songs/Month', 'Advanced Analytics', '42-Day Cycle', 'Priority Support'],
  },
  {
    id: 'legend',
    name: 'LEGEND',
    price: 60,
    platforms: 8,
    songs: 3,
    bgColor: 'bg-black',
    textColor: 'text-lime-400',
    accentColor: '#a3e635',
    features: ['ALL 8 Platforms', '3 Songs/Month', 'Full Analytics', '42-Day Cycle', 'Priority Support', 'Custom Scheduling'],
  },
];

// Helper to detect Spotify artist URL
function isSpotifyArtistUrl(url: string): boolean {
  const pattern = /(?:spotify:artist:|https:\/\/open\.spotify\.com\/artist\/)([a-zA-Z0-9]+)/;
  return pattern.test(url);
}

// Email validation regex
function isValidEmail(email: string): boolean {
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailPattern.test(email);
}

// Password strength checker - Medium strength: 8+ chars + letters + numbers
type PasswordStrength = 'weak' | 'medium' | 'strong';
function getPasswordStrength(password: string): { strength: PasswordStrength; message: string } {
  if (password.length < 8) {
    return { strength: 'weak', message: 'Too short (min 8 chars)' };
  }

  const hasLetters = /[a-zA-Z]/.test(password);
  const hasNumbers = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);

  // Strong: 8+ chars + uppercase + lowercase + numbers + special
  if (password.length >= 12 && hasUppercase && hasLowercase && hasNumbers && hasSpecial) {
    return { strength: 'strong', message: 'Strong password' };
  }

  // Medium: 8+ chars + letters + numbers (minimum requirement)
  if (hasLetters && hasNumbers) {
    return { strength: 'medium', message: 'Good password' };
  }

  // Weak: missing letters or numbers
  if (!hasLetters) {
    return { strength: 'weak', message: 'Add some letters' };
  }
  if (!hasNumbers) {
    return { strength: 'weak', message: 'Add some numbers' };
  }

  return { strength: 'weak', message: 'Add letters and numbers' };
}

export default function PricingV2() {
  const [selectedTier, setSelectedTier] = useState<'talent' | 'star' | 'legend' | null>(null);
  const [formData, setFormData] = useState({
    spotifyUrl: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validatedArtist, setValidatedArtist] = useState<ValidateArtistResponse | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-validate when Spotify URL is pasted
  useEffect(() => {
    const url = formData.spotifyUrl.trim();
    if (url && isSpotifyArtistUrl(url) && !validatedArtist) {
      validateArtist(url);
    }
  }, [formData.spotifyUrl]);

  const validateArtist = async (url: string) => {
    setIsValidating(true);
    setValidationError(null);

    try {
      const response = await spotifyAPI.validateArtist(url);
      if (response.data.success) {
        setValidatedArtist(response.data);
      } else {
        setValidationError('Could not find artist. Please check your URL.');
      }
    } catch (err: unknown) {
      console.error('Validation error:', err);
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setValidationError(axiosError.response?.data?.detail || 'Could not validate artist.');
      } else {
        setValidationError('Could not validate artist. Please try again.');
      }
    } finally {
      setIsValidating(false);
    }
  };

  const clearArtist = () => {
    setValidatedArtist(null);
    setFormData({ ...formData, spotifyUrl: '' });
    setValidationError(null);
  };

  // Validate email on blur
  const validateEmail = () => {
    if (formData.email && !isValidEmail(formData.email)) {
      setEmailError('Please enter a valid email address');
    } else {
      setEmailError(null);
    }
  };

  // Validate password confirmation
  const validatePasswordMatch = () => {
    if (formData.confirmPassword && formData.password !== formData.confirmPassword) {
      setPasswordError('Passwords do not match');
    } else {
      setPasswordError(null);
    }
  };

  // Password strength for current input
  const passwordStrength = formData.password ? getPasswordStrength(formData.password) : null;

  // Form is valid when:
  // - Artist is validated
  // - Email is valid
  // - Password meets medium strength (8+ chars + letters + numbers)
  // - Passwords match
  const isFormValid =
    validatedArtist !== null &&
    isValidEmail(formData.email) &&
    passwordStrength?.strength !== 'weak' &&
    formData.password === formData.confirmPassword &&
    formData.confirmPassword.length > 0;

  const handleSubmit = async () => {
    if (!selectedTier || !isFormValid || !validatedArtist) return;

    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Create user account with tier: "pending" + all spotify artist info
      const signupResponse = await authAPI.signUp(
        formData.email,
        formData.password,
        validatedArtist.artist_name, // Use validated artist name
        'pending',
        {
          spotify_artist_id: validatedArtist.artist_id,
          spotify_artist_name: validatedArtist.artist_name,
          spotify_artist_image_url: validatedArtist.artist_image_url,
          spotify_genres: validatedArtist.genres,
          spotify_followers: validatedArtist.followers,
          spotify_external_url: validatedArtist.external_url,
        }
      );

      const { user_id, token } = signupResponse.data;

      // Store token for the checkout request in localStorage
      // Note: Backend also sets HttpOnly cookie for production security
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', token);
      }

      // Step 2: Create Stripe checkout session with actual tier
      const checkoutResponse = await paymentAPI.createCheckoutSession(user_id, selectedTier);

      const { checkout_url } = checkoutResponse.data;

      // Step 3: Redirect to Stripe
      if (checkout_url) {
        window.location.href = checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (err: unknown) {
      console.error('Payment flow error:', err);

      // Handle specific error cases
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
        if (axiosError.response?.status === 409) {
          setError('An account with this email already exists. Please sign in instead.');
        } else if (axiosError.response?.data?.detail) {
          setError(axiosError.response.data.detail);
        } else {
          setError('Something went wrong. Please try again.');
        }
      } else {
        setError('Something went wrong. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">
      {/* Noise texture */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 md:px-12 md:py-6">
          <Link href="/" className="flex items-center gap-2">
            <Image
              src="/n-logo.png"
              alt="NOiSEMaKER"
              width={40}
              height={40}
              className="h-8 w-8 md:h-10 md:w-10"
            />
            <span className="text-lg font-black uppercase tracking-tight text-white">
              NOiSEMaKER
            </span>
          </Link>
          <Link
            href="/"
            className="border-2 border-white bg-transparent px-4 py-2 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-white hover:text-black"
          >
            Back
          </Link>
        </header>

        {/* Hero - Minimal */}
        <section className="border-b-4 border-white px-6 py-8 md:py-12">
          <div className="mx-auto max-w-6xl">
            <h1 className="text-5xl font-black uppercase leading-none tracking-tighter text-white md:text-7xl lg:text-8xl">
              PRICING
            </h1>
          </div>
        </section>

        {/* Global Error Message */}
        {error && (
          <div className="border-b-4 border-red-500 bg-red-500/20 px-6 py-4">
            <div className="mx-auto max-w-6xl">
              <p className="font-bold text-red-400">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm text-red-300 underline hover:text-white"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Tier Bands */}
        {tiers.map((tier, index) => {
          const isSelected = selectedTier === tier.id;
          const isStarTier = tier.id === 'star';

          return (
            <section
              key={tier.id}
              className={`border-b-4 border-white transition-all ${tier.bgColor} ${
                isSelected ? 'py-8' : 'py-6'
              }`}
            >
              <div className="mx-auto max-w-6xl px-6">
                {/* Clickable tier row */}
                <button
                  onClick={() => setSelectedTier(isSelected ? null : tier.id)}
                  className="flex w-full items-center justify-between text-left"
                  disabled={isLoading}
                >
                  <div className="flex items-baseline gap-4 md:gap-8">
                    {/* Tier number */}
                    <span
                      className={`text-6xl font-black md:text-8xl ${
                        isStarTier ? 'text-black/30' : 'text-white/20'
                      }`}
                    >
                      0{index + 1}
                    </span>

                    {/* Tier name */}
                    <div>
                      <h2 className={`text-3xl font-black uppercase md:text-5xl ${tier.textColor}`}>
                        {tier.name}
                      </h2>
                      <p className={`text-sm ${isStarTier ? 'text-black/60' : 'text-gray-500'}`}>
                        {tier.platforms} platforms • {tier.songs} songs/mo
                      </p>
                    </div>
                  </div>

                  {/* Price + Arrow */}
                  <div className="flex items-center gap-4 md:gap-8">
                    <div className="text-right">
                      <span className={`text-4xl font-black md:text-6xl ${tier.textColor}`}>
                        ${tier.price}
                      </span>
                      <span className={`text-lg ${isStarTier ? 'text-black/60' : 'text-gray-500'}`}>
                        /mo
                      </span>
                    </div>
                    <div
                      className={`flex h-12 w-12 items-center justify-center border-2 text-2xl font-black transition-transform ${
                        isStarTier ? 'border-black text-black' : 'border-white text-white'
                      } ${isSelected ? 'rotate-180' : ''}`}
                    >
                      ↓
                    </div>
                  </div>
                </button>

                {/* Expanded content */}
                {isSelected && (
                  <div className="mt-8 grid gap-8 border-t-2 border-dashed border-current pt-8 md:grid-cols-2">
                    {/* Features */}
                    <div>
                      <h3
                        className={`mb-4 text-sm font-black uppercase tracking-widest ${
                          isStarTier ? 'text-black/60' : 'text-gray-500'
                        }`}
                      >
                        What you get
                      </h3>
                      <ul className="grid grid-cols-2 gap-2">
                        {tier.features.map((feature, i) => (
                          <li
                            key={i}
                            className={`flex items-center gap-2 text-sm font-bold ${
                              isStarTier ? 'text-black' : 'text-white'
                            }`}
                          >
                            <span style={{ color: tier.accentColor }}>★</span>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Form */}
                    <div
                      className={`border-4 p-6 ${
                        isStarTier ? 'border-black bg-white' : 'border-white bg-black'
                      }`}
                    >
                      <h3
                        className={`mb-4 text-lg font-black uppercase ${
                          isStarTier ? 'text-black' : 'text-white'
                        }`}
                      >
                        Sign Up
                      </h3>

                      <div className="space-y-3">
                        {/* Spotify Artist URL - Expandable Card */}
                        <div>
                          {validatedArtist ? (
                            // Validated artist card
                            <div
                              className={`flex items-center gap-3 border-2 p-3 ${
                                isStarTier
                                  ? 'border-lime-400 bg-lime-400/10'
                                  : 'border-lime-400 bg-lime-400/10'
                              }`}
                            >
                              {validatedArtist.artist_image_url && (
                                <img
                                  src={validatedArtist.artist_image_url}
                                  alt={validatedArtist.artist_name}
                                  className="h-12 w-12 rounded-full object-cover"
                                />
                              )}
                              <div className="flex-1">
                                <p className={`text-sm font-black ${isStarTier ? 'text-black' : 'text-white'}`}>
                                  {validatedArtist.artist_name}
                                </p>
                                <p className="text-xs text-lime-400">
                                  ✓ Verified on Spotify
                                  {validatedArtist.followers && ` • ${validatedArtist.followers.toLocaleString()} followers`}
                                </p>
                              </div>
                              <button
                                type="button"
                                onClick={clearArtist}
                                disabled={isLoading}
                                className={`text-xs font-bold underline ${
                                  isStarTier ? 'text-black/60 hover:text-black' : 'text-gray-400 hover:text-white'
                                }`}
                              >
                                Change
                              </button>
                            </div>
                          ) : (
                            // Spotify URL input
                            <>
                              <div className="relative">
                                <input
                                  type="text"
                                  value={formData.spotifyUrl}
                                  onChange={(e) => setFormData({ ...formData, spotifyUrl: e.target.value })}
                                  placeholder="Paste your Spotify artist link"
                                  disabled={isLoading || isValidating}
                                  className={`w-full border-2 px-3 py-2 pr-10 text-sm font-bold outline-none disabled:opacity-50 ${
                                    validationError
                                      ? 'border-red-500'
                                      : isStarTier
                                        ? 'border-black bg-white text-black placeholder-gray-400'
                                        : 'border-white bg-black text-white placeholder-gray-600'
                                  }`}
                                />
                                {isValidating && (
                                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-lime-400 border-t-transparent" />
                                  </div>
                                )}
                              </div>
                              {validationError ? (
                                <p className="mt-1 text-xs text-red-400">{validationError}</p>
                              ) : (
                                <p className={`mt-1 text-xs ${isStarTier ? 'text-black/50' : 'text-gray-500'}`}>
                                  e.g. https://open.spotify.com/artist/...
                                </p>
                              )}
                            </>
                          )}
                        </div>

                        {/* Email input with validation */}
                        <div>
                          <input
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            onBlur={validateEmail}
                            placeholder="Email"
                            disabled={isLoading}
                            className={`w-full border-2 px-3 py-2 text-sm font-bold outline-none disabled:opacity-50 ${
                              emailError
                                ? 'border-red-500'
                                : isStarTier
                                  ? 'border-black bg-white text-black placeholder-gray-400'
                                  : 'border-white bg-black text-white placeholder-gray-600'
                            }`}
                          />
                          {emailError && (
                            <p className="mt-1 text-xs text-red-400">{emailError}</p>
                          )}
                        </div>

                        {/* Password input with strength indicator */}
                        <div>
                          <input
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            placeholder="Password"
                            disabled={isLoading}
                            className={`w-full border-2 px-3 py-2 text-sm font-bold outline-none disabled:opacity-50 ${
                              isStarTier
                                ? 'border-black bg-white text-black placeholder-gray-400'
                                : 'border-white bg-black text-white placeholder-gray-600'
                            }`}
                          />
                          {/* Password strength indicator */}
                          {passwordStrength && (
                            <div className="mt-1 flex items-center gap-2">
                              <div className="flex h-1 flex-1 gap-1">
                                <div
                                  className={`h-full flex-1 ${
                                    passwordStrength.strength === 'weak'
                                      ? 'bg-red-500'
                                      : passwordStrength.strength === 'medium'
                                        ? 'bg-yellow-500'
                                        : 'bg-lime-500'
                                  }`}
                                />
                                <div
                                  className={`h-full flex-1 ${
                                    passwordStrength.strength === 'medium'
                                      ? 'bg-yellow-500'
                                      : passwordStrength.strength === 'strong'
                                        ? 'bg-lime-500'
                                        : isStarTier
                                          ? 'bg-black/20'
                                          : 'bg-white/20'
                                  }`}
                                />
                                <div
                                  className={`h-full flex-1 ${
                                    passwordStrength.strength === 'strong'
                                      ? 'bg-lime-500'
                                      : isStarTier
                                        ? 'bg-black/20'
                                        : 'bg-white/20'
                                  }`}
                                />
                              </div>
                              <span
                                className={`text-xs ${
                                  passwordStrength.strength === 'weak'
                                    ? 'text-red-400'
                                    : passwordStrength.strength === 'medium'
                                      ? 'text-yellow-400'
                                      : 'text-lime-400'
                                }`}
                              >
                                {passwordStrength.message}
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Confirm password input */}
                        <div>
                          <input
                            type="password"
                            value={formData.confirmPassword}
                            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                            onBlur={validatePasswordMatch}
                            placeholder="Confirm Password"
                            disabled={isLoading}
                            className={`w-full border-2 px-3 py-2 text-sm font-bold outline-none disabled:opacity-50 ${
                              passwordError
                                ? 'border-red-500'
                                : isStarTier
                                  ? 'border-black bg-white text-black placeholder-gray-400'
                                  : 'border-white bg-black text-white placeholder-gray-600'
                            }`}
                          />
                          {passwordError && (
                            <p className="mt-1 text-xs text-red-400">{passwordError}</p>
                          )}
                        </div>
                      </div>

                      {isFormValid ? (
                        <button
                          onClick={handleSubmit}
                          disabled={isLoading}
                          className={`mt-4 w-full border-4 py-3 text-sm font-black uppercase tracking-wider transition-all disabled:cursor-not-allowed disabled:opacity-50 ${
                            isStarTier
                              ? 'border-black bg-lime-400 text-black hover:bg-lime-300'
                              : 'border-white bg-fuchsia-500 text-black hover:bg-fuchsia-400'
                          }`}
                        >
                          {isLoading ? 'PROCESSING...' : 'PAY NOW & MAKE NOISE →'}
                        </button>
                      ) : (
                        <p
                          className={`mt-4 text-center text-xs ${
                            isStarTier ? 'text-black/50' : 'text-gray-500'
                          }`}
                        >
                          Fill all fields to continue
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </section>
          );
        })}

        {/* Bottom CTA if nothing selected */}
        {!selectedTier && (
          <section className="bg-white px-6 py-16 text-center">
            <p className="text-xl font-black uppercase text-black">
              ↑ TAP A PLAN TO GET STARTED ↑
            </p>
          </section>
        )}

        {/* Footer */}
        <footer className="border-t-4 border-white bg-black px-6 py-6 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            © 2026 NOiSEMaKER by DooWopp
          </p>
        </footer>
      </div>
    </main>
  );
}
