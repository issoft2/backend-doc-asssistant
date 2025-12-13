# 1) Build stage
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build    # produces /app/dist

# 2) Runtime stage: serve static files
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: SPA routing support
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
