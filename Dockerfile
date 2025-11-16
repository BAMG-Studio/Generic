# Dockerfile for ForgeTrace Production

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt requirements-optional.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-optional.txt

# Copy application code
COPY forgetrace/ ./forgetrace/
COPY scripts/ ./scripts/
COPY models/ ./models/
COPY config.yaml setup.py ./

# Install ForgeTrace
RUN pip install --no-cache-dir -e .

# Create directories for output
RUN mkdir -p /output /cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FORGETRACE_CACHE_DIR=/cache

# Default command
ENTRYPOINT ["forgetrace"]
CMD ["--help"]
