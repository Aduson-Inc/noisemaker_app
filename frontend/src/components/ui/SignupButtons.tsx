'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import MarqueeButton from './MarqueeButton';

interface SignupButtonsProps {
  variant?: 'hero' | 'cta';
  className?: string;
}

export default function SignupButtons({ variant = 'hero', className = '' }: SignupButtonsProps) {
  const router = useRouter();
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGoogleSignIn = () => {
    localStorage.setItem('oauth_provider', 'google');
    signIn('google', { callbackUrl: '/pricing' });
  };

  const handleFacebookSignIn = () => {
    localStorage.setItem('oauth_provider', 'facebook');
    signIn('facebook', { callbackUrl: '/pricing' });
  };

  const handleEmailSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/email-signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Signup failed');
      }

      // Store auth data for pricing page
      if (data.user_id) {
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('signup_method', 'email');
      }
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
      }

      router.push('/pricing');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <div className="space-y-4">
        {/* Google OAuth Button */}
        <button
          onClick={handleGoogleSignIn}
          className="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-300 rounded-lg py-4 px-6 font-medium text-gray-800 hover:bg-gray-50 hover:border-gray-400 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
        >
          <svg className="w-6 h-6" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span className="font-semibold">Continue with Google</span>
        </button>

        {/* Facebook OAuth Button */}
        <button
          onClick={handleFacebookSignIn}
          className="w-full flex items-center justify-center gap-3 bg-[#1877F2] rounded-lg py-4 px-6 text-white font-medium hover:bg-[#166FE5] transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
          </svg>
          <span className="font-semibold">Continue with Facebook</span>
        </button>
      </div>

      {/* More Options Toggle */}
      <button
        onClick={() => setShowEmailForm(!showEmailForm)}
        className="mt-6 text-gray-400 text-sm hover:text-gray-200 transition-colors duration-300 flex items-center justify-center w-full gap-2"
      >
        <span className="uppercase tracking-wider">More Options</span>
        <span className="text-xs">{showEmailForm ? '▲' : '▼'}</span>
      </button>

      {/* Email/Password Form */}
      {showEmailForm && (
        <form onSubmit={handleEmailSignup} className="mt-6 space-y-4 animate-fade-in">
          {error && (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-3">
              <p className="text-red-400 text-sm text-center">{error}</p>
            </div>
          )}

          <div>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-white/5 border-2 border-gray-600 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:border-[var(--color-cyan)] focus:outline-none transition-colors duration-300"
            />
          </div>

          <div>
            <input
              type="password"
              placeholder="Create password (min 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full bg-white/5 border-2 border-gray-600 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:border-[var(--color-cyan)] focus:outline-none transition-colors duration-300"
            />
          </div>

          <MarqueeButton type="submit" disabled={isLoading} variant="primary" className="w-full">
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </MarqueeButton>

          <p className="text-xs text-gray-500 text-center mt-4">
            By continuing, you agree to our{' '}
            <a href="/terms" className="text-[var(--color-cyan)] hover:underline">
              Terms
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-[var(--color-cyan)] hover:underline">
              Privacy Policy
            </a>
          </p>
        </form>
      )}
    </div>
  );
}
