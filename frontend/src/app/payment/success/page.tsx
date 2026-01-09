'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { paymentAPI } from '@/lib/api';

/**
 * Payment Success Page
 *
 * Stripe redirects here after successful checkout:
 * /payment/success?session_id=cs_xxx&user_id=xxx
 *
 * This page:
 * 1. Extracts session_id from URL
 * 2. Calls POST /api/payment/confirm to verify payment
 * 3. Stores new JWT token
 * 4. Redirects to onboarding
 */

type PageStatus = 'loading' | 'success' | 'error';

function PaymentSuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [status, setStatus] = useState<PageStatus>('loading');
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    const confirmPayment = async () => {
      const sessionId = searchParams.get('session_id');

      if (!sessionId) {
        setStatus('error');
        setError('No session ID found. Please contact support.');
        return;
      }

      try {
        // Confirm payment with backend
        const response = await paymentAPI.confirmPayment(sessionId);

        if (response.data.success) {
          // Store new JWT token in both localStorage and cookie
          if (typeof window !== 'undefined' && response.data.token) {
            localStorage.setItem('auth_token', response.data.token);
            // Set cookie for middleware (7 days expiry)
            document.cookie = `auth_token=${response.data.token}; path=/; max-age=604800; SameSite=Lax`;
          }

          setStatus('success');

          // Start countdown and redirect
          let count = 5;
          const interval = setInterval(() => {
            count--;
            setCountdown(count);
            if (count === 0) {
              clearInterval(interval);
              router.push('/milestone/first_payment');
            }
          }, 1000);

          return () => clearInterval(interval);
        } else {
          throw new Error(response.data.message || 'Payment confirmation failed');
        }
      } catch (err: unknown) {
        console.error('Payment confirmation error:', err);
        setStatus('error');

        if (err && typeof err === 'object' && 'response' in err) {
          const axiosError = err as { response?: { data?: { detail?: string } } };
          setError(axiosError.response?.data?.detail || 'Failed to confirm payment');
        } else {
          setError('Failed to confirm payment. Please contact support.');
        }
      }
    };

    confirmPayment();
  }, [searchParams, router]);

  return (
    <>
      {/* Loading State */}
      {status === 'loading' && (
        <div className="space-y-6">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-fuchsia-500 border-t-transparent" />
          <h1 className="text-2xl font-black uppercase text-white md:text-3xl">
            CONFIRMING PAYMENT...
          </h1>
          <p className="text-gray-400">Please wait while we verify your subscription.</p>
        </div>
      )}

      {/* Success State */}
      {status === 'success' && (
        <div className="space-y-6">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border-4 border-lime-400 bg-lime-400/20">
            <span className="text-4xl text-lime-400">✓</span>
          </div>
          <h1 className="text-3xl font-black uppercase text-white md:text-4xl">
            PAYMENT
            <br />
            <span className="text-lime-400">SUCCESSFUL!</span>
          </h1>
          <p className="text-lg text-gray-300">
            Welcome to NOiSEMaKER! Your subscription is now active.
          </p>
          <div className="border-4 border-white bg-white/10 p-4">
            <p className="text-sm font-bold uppercase text-gray-400">
              Redirecting to setup in
            </p>
            <p className="text-4xl font-black text-fuchsia-400">{countdown}</p>
          </div>
          <Link
            href="/milestone/first_payment"
            className="mt-4 inline-block border-4 border-white bg-fuchsia-500 px-8 py-4 text-lg font-black uppercase tracking-wider text-black transition-all hover:bg-fuchsia-400"
          >
            CONTINUE NOW →
          </Link>
        </div>
      )}

      {/* Error State */}
      {status === 'error' && (
        <div className="space-y-6">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border-4 border-red-500 bg-red-500/20">
            <span className="text-4xl text-red-500">✕</span>
          </div>
          <h1 className="text-3xl font-black uppercase text-white md:text-4xl">
            SOMETHING
            <br />
            <span className="text-red-500">WENT WRONG</span>
          </h1>
          <p className="text-lg text-gray-300">{error}</p>
          <div className="flex flex-col gap-4">
            <Link
              href="/pricing"
              className="inline-block border-4 border-white bg-white px-8 py-4 text-lg font-black uppercase tracking-wider text-black transition-all hover:bg-gray-200"
            >
              TRY AGAIN
            </Link>
            <a
              href="mailto:support@doowopp.com"
              className="text-sm text-gray-500 underline hover:text-white"
            >
              Contact Support
            </a>
          </div>
        </div>
      )}
    </>
  );
}

function LoadingFallback() {
  return (
    <div className="space-y-6">
      <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-fuchsia-500 border-t-transparent" />
      <h1 className="text-2xl font-black uppercase text-white md:text-3xl">
        LOADING...
      </h1>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <main className="relative flex min-h-screen w-full items-center justify-center overflow-x-hidden bg-black">
      {/* Noise texture */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10 w-full max-w-lg px-6 text-center">
        {/* Logo */}
        <div className="mb-8 flex justify-center">
          <Image
            src="/n-logo.png"
            alt="NOiSEMaKER"
            width={80}
            height={80}
            className="h-16 w-16 md:h-20 md:w-20"
          />
        </div>

        <Suspense fallback={<LoadingFallback />}>
          <PaymentSuccessContent />
        </Suspense>
      </div>
    </main>
  );
}
