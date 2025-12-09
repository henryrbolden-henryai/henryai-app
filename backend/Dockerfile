# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (improves caching)
COPY backend/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY backend/ .

# Expose port
EXPOSE 8000

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
