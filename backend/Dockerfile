# Backend Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt ./backend/

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the document_generator module (required by backend)
COPY document_generator/ ./document_generator/

# Copy backend code
COPY backend/ ./backend/

# Set working directory to backend
WORKDIR /app/backend

# Expose port (Railway sets PORT env variable)
EXPOSE 8000

# Run the application (Railway sets PORT env variable)
CMD uvicorn backend:app --host 0.0.0.0 --port ${PORT:-8000}
