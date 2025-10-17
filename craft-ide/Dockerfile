# Stage 1: Build the React application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./
COPY package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:1.25-alpine

# Copy the build output from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the nginx config file
# Note: We will need to create this nginx.conf file next.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]