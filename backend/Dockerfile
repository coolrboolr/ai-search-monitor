# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for pgvector/psycopg2 if building from source, and general utility)
# libpq-dev is often needed for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files first for better caching
COPY pyproject.toml .
# If you had a requirements.txt, you'd copy it here. 
# Since we are using pyproject.toml, we can install directly or generate requirements.
# We'll install the package in editable mode or just dependencies.
# Installing dependencies from pyproject.toml:
RUN pip install --no-cache-dir .

# Copy the rest of the application code
COPY src/ ./src/

# Install Playwright and browser deps
# This is heavy but needed for scraping
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium

# Prefetch embedding model at build-time so it’s baked into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Create a non-root user for security (optional but recommended for Render)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Default command (can be overridden by Render for the Cron Job)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
