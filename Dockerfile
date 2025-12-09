FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV PORT=8000

CMD ["uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "8000"]
