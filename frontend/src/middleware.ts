import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const TOKEN_KEY = "alphacon_token";
const AUTH_PATHS = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(TOKEN_KEY)?.value;

  const isAuthPath = AUTH_PATHS.some((p) => pathname.startsWith(p));

  if (isAuthPath) {
    // Already authenticated — bounce to the app
    if (token) {
      return NextResponse.redirect(new URL("/intelligence", request.url));
    }
    return NextResponse.next();
  }

  // Everything else requires a token
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  // Run on all routes except Next.js internals and static files
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
