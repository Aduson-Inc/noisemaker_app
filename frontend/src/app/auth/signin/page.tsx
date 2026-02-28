'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';

export default function SignInPage() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const canSubmit = email.trim().length > 0 && password.length > 0 && !isSubmitting;

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setError(null);
    setIsSubmitting(true);

    try {
      const response = await authAPI.signIn(email.trim(), password);
      const data = response.data;

      // Store token in localStorage + cookie (matches payment success pattern)
      if (typeof window !== 'undefined' && data.token) {
        localStorage.setItem('auth_token', data.token);
        document.cookie = `auth_token=${data.token}; path=/; max-age=604800; SameSite=Lax`;
      }

      // Backend returns redirect_to with full smart routing:
      // - No platforms → /onboarding/how-it-works
      // - Platforms but no songs → /onboarding/how-it-works-2
      // - Pending milestone → /milestone/{type}
      // - Onboarding complete → /dashboard
      const redirectTo = data.redirect_to || '/dashboard';
      router.push(redirectTo);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(detail || 'Invalid email or password');
      setIsSubmitting(false);
    }
  };

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">
      {/* Noise texture overlay */}
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
            href="/pricing"
            className="text-xs font-bold uppercase tracking-widest text-gray-500 transition-colors hover:text-white"
          >
            Create Account
          </Link>
        </header>

        {/* Divider */}
        <div className="border-b-4 border-white" />

        {/* Sign In Form */}
        <div className="flex min-h-[80vh] flex-col items-center justify-center px-6">
          <div className="w-full max-w-md">
            {/* Title */}
            <h1 className="mb-2 text-center text-5xl font-black uppercase tracking-tighter text-white md:text-6xl">
              Welcome<br />
              <span className="text-lime-400">Back</span>
            </h1>
            <p className="mb-10 text-center text-xs font-bold uppercase tracking-widest text-gray-500">
              Sign in to your account
            </p>

            {/* Error */}
            {error && (
              <div className="mb-6 border-l-4 border-red-500 bg-red-500/10 px-4 py-3">
                <p className="text-sm font-bold text-red-400">{error}</p>
              </div>
            )}

            <form onSubmit={handleSignIn} className="space-y-6">
              {/* Email */}
              <div>
                <label className="mb-2 block text-xs font-black uppercase tracking-widest text-gray-400">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                  className="w-full border-4 border-white bg-black px-4 py-3 text-sm font-bold text-white placeholder-gray-600 outline-none transition-colors focus:border-lime-400"
                />
              </div>

              {/* Password */}
              <div>
                <label className="mb-2 block text-xs font-black uppercase tracking-widest text-gray-400">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Your password"
                    autoComplete="current-password"
                    className="w-full border-4 border-white bg-black px-4 py-3 pr-16 text-sm font-bold text-white placeholder-gray-600 outline-none transition-colors focus:border-lime-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-black uppercase tracking-widest text-gray-500 transition-colors hover:text-white"
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={!canSubmit}
                className={`w-full border-4 py-4 text-sm font-black uppercase tracking-widest transition-all ${
                  canSubmit
                    ? 'border-lime-400 bg-lime-400 text-black hover:bg-transparent hover:text-lime-400'
                    : 'cursor-not-allowed border-gray-700 bg-gray-700 text-gray-500'
                }`}
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-3">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-black border-t-transparent" />
                    Signing In...
                  </span>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>

            {/* Bottom link */}
            <p className="mt-8 text-center text-xs font-bold uppercase tracking-widest text-gray-600">
              Don&apos;t have an account?{' '}
              <Link href="/pricing" className="text-lime-400 transition-colors hover:text-white">
                Get Started
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t-4 border-white/20 bg-black px-6 py-6 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            &copy; 2026 NOiSEMaKER by DooWopp
          </p>
        </footer>
      </div>
    </main>
  );
}
