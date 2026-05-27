# ── Stage 1: Base image ────────────────────────────────────────────────────────
# We use a slim Python image to keep the container small
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies FIRST (before copying code)
# This is a Docker best practice — if only code changes, dependencies
# are already cached and don't need to reinstall (saves time)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app code
COPY . .

# Expose port 8000 so Docker knows our app listens here
EXPOSE 8000

# Health check — Docker will ping this every 30s to see if container is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start the app using uvicorn (production ASGI server for FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
