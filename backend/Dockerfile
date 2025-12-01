# /backend/Dockerfile
# Python Flask Backend for Gantt Chart Application

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
echo "Starting Gunicorn server..."\n\
exec gunicorn -b 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Run entrypoint
CMD ["/entrypoint.sh"]

