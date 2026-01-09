// Next.js Middleware for Protected Routes
import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/onboarding/:path*',
    '/milestone/:path*'
  ]
};

export default async function middleware(request: NextRequest) {
  // Check for NextAuth session token
  const nextAuthToken = await getToken({
    req: request,
    secret: process.env.NEXTAUTH_SECRET,
  });

  // Check for custom auth token cookie (from email signup)
  const customAuthToken = request.cookies.get('auth_token');

  // Allow access if either auth method is present
  if (nextAuthToken || customAuthToken) {
    return NextResponse.next();
  }

  // No authentication found, redirect to home
  return NextResponse.redirect(new URL('/', request.url));
}
