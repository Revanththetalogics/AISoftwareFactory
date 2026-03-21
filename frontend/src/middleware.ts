import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { isValidToken } from '@/lib/auth/token-validation';

/**
 * Enterprise-grade Next.js middleware for authentication
 * Runs on EVERY request before page load
 */

// Public routes that don't require authentication
const PUBLIC_ROUTES = [
  '/login',
  '/unauthorized',
  '/favicon.ico',
];

// Route prefixes that should be public
const PUBLIC_PREFIXES = [
  '/_next',
  '/public',
  '/api/auth', // Allow auth API routes if any
];

// File extensions that should bypass middleware
const STATIC_FILE_EXTENSIONS = [
  '.ico',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.svg',
  '.webp',
  '.css',
  '.js',
  '.woff',
  '.woff2',
  '.ttf',
  '.eot',
];

/**
 * Check if the path is a public route
 */
function isPublicRoute(pathname: string): boolean {
  // Check exact public routes
  if (PUBLIC_ROUTES.includes(pathname)) {
    return true;
  }

  // Check public prefixes
  for (const prefix of PUBLIC_PREFIXES) {
    if (pathname.startsWith(prefix)) {
      return true;
    }
  }

  // Check static file extensions
  for (const ext of STATIC_FILE_EXTENSIONS) {
    if (pathname.endsWith(ext)) {
      return true;
    }
  }

  return false;
}

/**
 * Add security headers to response
 */
function addSecurityHeaders(response: NextResponse): NextResponse {
  // Prevent clickjacking
  response.headers.set('X-Frame-Options', 'DENY');
  
  // Prevent MIME type sniffing
  response.headers.set('X-Content-Type-Options', 'nosniff');
  
  // XSS protection (legacy but still useful for older browsers)
  response.headers.set('X-XSS-Protection', '1; mode=block');
  
  // Referrer policy
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  // Content Security Policy for additional protection
  response.headers.set(
    'Permissions-Policy',
    'camera=(), microphone=(), geolocation=()'
  );

  // Content Security Policy
  response.headers.set(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
  );

  // HTTP Strict Transport Security
  response.headers.set(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains'
  );

  return response;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Get auth token from cookies
  const authToken = request.cookies.get('auth_token')?.value;
  const isAuthenticated = isValidToken(authToken);

  // Handle public routes
  if (isPublicRoute(pathname)) {
    // If user is authenticated and trying to access login page, redirect to dashboard
    if (pathname === '/login' && isAuthenticated) {
      const dashboardUrl = new URL('/dashboard', request.url);
      const response = NextResponse.redirect(dashboardUrl);
      return addSecurityHeaders(response);
    }
    
    // Allow access to public routes
    const response = NextResponse.next();
    return addSecurityHeaders(response);
  }

  // Protected routes - require authentication
  if (!isAuthenticated) {
    // Build login URL with return path
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnUrl', pathname);
    
    const response = NextResponse.redirect(loginUrl);
    return addSecurityHeaders(response);
  }

  // User is authenticated - allow access
  const response = NextResponse.next();
  return addSecurityHeaders(response);
}

/**
 * Matcher configuration
 * Excludes static assets, _next, and other files that shouldn't be processed
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes) - handled separately
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js|woff|woff2|ttf|eot)$).*)',
  ],
};
