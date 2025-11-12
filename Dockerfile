# Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the the app to WORKDIR/app
COPY . .

EXPOSE 8000
# Bind gunicorn to 0.0.0.0:8000 so it’s reachable outside the container
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
