FROM python:3.12-slim

# Install system dependencies (build-essential needed for some minor C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better caching
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# The code will be mounted at runtime via docker-compose, but we can copy it here too
COPY . .

CMD ["python", "agents/run_demo.py"]
