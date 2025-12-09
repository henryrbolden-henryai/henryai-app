FROM python:3.10-slim

WORKDIR /app

# Install backend requirements
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and the document generator folder
COPY backend /app/backend
COPY document_generator /app/document_generator

# Make sure Python can import from /app
ENV PYTHONPATH="/app"

# Start the API server
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
