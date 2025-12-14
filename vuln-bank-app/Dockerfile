FROM python:3.9-slim

USER root

RUN apt-get update && apt-get install -y \
    net-tools \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos toda la carpeta 'app' (que contiene app.py, database.py, static/ y templates/)
COPY app/ .

# Crear el directorio de uploads que se usará para el LFI.
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

EXPOSE 8080

CMD ["python", "app.py"]
