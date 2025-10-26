# Dockerfile for FastAPI Backend

# Use a Python base image
FROM python:3.13-slim-bookworm

# Set working directory in the container
WORKDIR /app

# Copy pyproject.toml and uv.lock (if using uv) first to leverage Docker cache
COPY pyproject.toml uv.lock* ./ 

# Install dependencies
# Using pip to install from pyproject.toml
RUN pip install --no-cache-dir ".[all]" # Install all dependencies including optional ones

# Install curl for debugging/testing purposes inside the container
RUN apt-get update && apt-get install -y curl iputils-ping --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
