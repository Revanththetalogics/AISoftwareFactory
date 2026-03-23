# Stage 1: Build Next.js to extract static assets.
# Build context is the repo root (docker build -f nginx/Dockerfile .).
# This stage uses identical build args as the frontend Dockerfile so
# content-hashed filenames are identical in both images.
FROM node:20-alpine AS frontend-builder
WORKDIR /app

ARG NEXT_PUBLIC_API_URL=https://ai-staging.thetalogics.com/api
ARG NEXT_PUBLIC_WS_URL=wss://ai-staging.thetalogics.com/ws

ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}

# Copy frontend source from repo root context
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ .
RUN rm -rf .next/cache && npm run build

# Stage 2: nginx with static assets baked in — zero runtime dependency.
# /_next/static/ and /public/ are served directly by nginx at full disk speed.
# The Node.js SSR container handles only SSR page requests.
FROM nginx:alpine AS runner

# Embed the nginx config directly — no host volume mount required.
COPY nginx.conf /etc/nginx/conf.d/00-ai-factory.conf

# Bake static assets into the image filesystem.
# nginx.conf aliases /_next/static/ → /app/static/_next/static/
# and /public/ → /app/static/public/
COPY --from=frontend-builder /app/.next/static /app/static/_next/static
COPY --from=frontend-builder /app/public        /app/static/public

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
