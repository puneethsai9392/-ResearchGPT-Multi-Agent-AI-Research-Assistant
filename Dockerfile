# Python 3.12 Slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create persistent data directory
RUN mkdir -p /app/data

# Expose FastAPI and Streamlit ports
EXPOSE 8000
EXPOSE 8501

# Default command starts FastAPI backend
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
