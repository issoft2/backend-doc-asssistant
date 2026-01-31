# Stage 1: Build Vue frontend
FROM node:20-alpine AS builder

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Production-ready Nginx (Internal Worker)
FROM nginx:alpine

RUN apk add --no-cache curl

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# --- REFINEMENT HERE ---
# Instead of nginx.conf (the SSL one), we copy a new internal-only file
COPY nginx/internal.conf /etc/nginx/conf.d/default.conf

# Copy built frontend assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Only expose 80. The "Master" Nginx container handles the 443/SSL side.
EXPOSE 80

# Basic healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]