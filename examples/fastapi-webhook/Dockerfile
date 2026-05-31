# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Presscart must reach this from the internet (use a tunnel for local dev).
EXPOSE 8000

# A single worker keeps the in-memory de-dupe set coherent. Only scale to
# multiple workers/replicas after moving de-dupe to a shared store.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
