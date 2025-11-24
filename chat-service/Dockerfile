# Base image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /usr/src/chat-service

# Python runtime flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install alembic

# Copy the application code
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY app ./app
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Expose FastAPI port
EXPOSE 5002

# Entrypoint script
ENTRYPOINT ["/usr/src/chat-service/entrypoint.sh"]

# FastAPI server with auto-reload
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "5002"]
