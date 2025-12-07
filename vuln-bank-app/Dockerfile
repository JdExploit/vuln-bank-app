FROM python:3.9-slim

# Vulnerable por diseño
USER root

RUN apt-get update && apt-get install -y \
    sqlite3 \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN mkdir -p /app/uploads && \
    chmod 777 /app/uploads && \
    chmod 777 /app && \
    echo "Test file for path traversal" > /app/uploads/test.txt

EXPOSE 8080

CMD ["python", "app.py"]