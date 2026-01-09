'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export function useAuth(redirectTo = '/auth/signin') {
  const router = useRouter();

  useEffect(() => {
    // Check for auth token
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      router.push(redirectTo);
    }
  }, [router, redirectTo]);

  return { isAuthenticated: !!localStorage.getItem('auth_token') };
}

export function checkAuth() {
  if (typeof window !== 'undefined') {
    return !!localStorage.getItem('auth_token');
  }
  return false;
}
