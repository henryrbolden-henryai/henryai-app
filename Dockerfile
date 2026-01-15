FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend code
COPY backend /app/backend
COPY document_generator /app/document_generator

ENV PORT=8000

CMD ["uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "300"]
