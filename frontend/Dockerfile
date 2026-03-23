FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Accept build arguments for API URLs
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL

# Set as environment variables for build
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-https://ai-staging.thetalogics.com/api}
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL:-wss://ai-staging.thetalogics.com/ws}

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Clear any cached data and build the application
RUN rm -rf .next/cache && npm run build

# Production image - standalone mode
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy public folder
COPY --from=builder /app/public ./public

# Copy standalone server and static files
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Pre-populate a staging directory with built assets.
# At container startup, these are copied into the named volume (/app/static)
# shared with nginx, which serves /_next/static/ and /public/ directly.
RUN mkdir -p /app/static-seed /app/static && chown -R nextjs:nodejs /app/static-seed /app/static
COPY --from=builder --chown=nextjs:nodejs /app/.next/static /app/static-seed/_next/static
COPY --from=builder --chown=nextjs:nodejs /app/public /app/static-seed/public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Entrypoint: seed the shared volume with static assets, then start the SSR server.
# The named volume (/app/static) is empty on first mount; cp seeds it from the image.
CMD sh -c "cp -rn /app/static-seed/. /app/static/ && node server.js"
