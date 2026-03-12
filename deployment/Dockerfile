# Dockerfile for AI Employee Platinum Tier
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY platinum/requirements.txt /app/platinum/requirements.txt
COPY web_dashboard/requirements.txt /app/web_dashboard/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/platinum/requirements.txt
RUN pip install --no-cache-dir -r /app/web_dashboard/requirements.txt

# Copy application code
COPY platinum/ /app/platinum/
COPY web_dashboard/ /app/web_dashboard/
COPY watchers/ /app/watchers/
COPY orchestrator.py /app/

# Create vault directory
RUN mkdir -p /app/vault

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose ports
EXPOSE 7860 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860 || exit 1

# Default command
CMD ["python", "web_dashboard/app.py", "/app/vault", "--port", "7860"]
