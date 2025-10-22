# --- Stage 1: Build stage ---
FROM node:20-alpine AS builder
WORKDIR /app

# Install dependencies
COPY docs/package*.json ./
RUN npm ci

# Copy all source files
COPY ./docs ./

# Build the VitePress docs (from /docs)
RUN npm run build

# --- Stage 2: Production stage ---
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html

# Copy only the built VitePress output
COPY --from=builder /app/.vitepress/dist ./

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]