FROM python:3.12-slim

WORKDIR /app

WORKDIR /app

# Install dependencies first for better caching
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# The code will be mounted at runtime via docker-compose, but we can copy it here too
COPY . .

CMD ["python", "agents/run_demo.py"]
