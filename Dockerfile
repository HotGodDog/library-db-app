# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install the system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency files
COPY requirements.txt requirements.lock ./

# Install the dependencies
RUN if [ -f requirements.lock ]; then \
        echo "Installing from requirements.lock" && \
        pip install --no-cache-dir --extra-index-url https://test.pypi.org/simple/ -r requirements.lock; \
    else \
        echo "Installing from requirements.txt" && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy the app
COPY src/ ./src/
COPY Makefile .

# Enviroment variables
ENV FLASK_APP=src/app
ENV PYTHONPATH=/app/src
ENV LIBRARY_DB_PATH=/data/library.db

# Create a directory for SQLite
RUN mkdir -p /data

# Checking the app
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]