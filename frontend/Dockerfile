# /frontend/Dockerfile
# Vue 3 Frontend for Gantt Chart Application

# Build stage
FROM node:24 AS build

WORKDIR /app

# Build argument for API URL
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy package files
COPY package*.json ./

# Install dependencies (npm install for first build, or use npm ci if package-lock.json exists)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build for production (vite will pick up VITE_* env vars)
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

