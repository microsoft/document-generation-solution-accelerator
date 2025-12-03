FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY content-gen/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY content-gen/src/app.py .
COPY content-gen/src/hypercorn.conf.py .
COPY content-gen/src/backend/ ./backend/

# Expose port
EXPOSE 8000

# Run with hypercorn
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8000"]
