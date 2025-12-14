# Usa una versión de Python estable y ligera
FROM python:3.9-slim

# Nota: El usuario root es intencional para las pruebas de escalada de privilegios y CMDi.
USER root

# Instalación de herramientas de prueba y dependencias de la aplicación
RUN apt-get update && apt-get install -y \
    # net-tools para 'ping' y otras utilidades
    net-tools \
    # curl para probar SSRF
    curl \
    # sqlite3 para la gestión de la DB
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Definimos el directorio de trabajo
WORKDIR /app

# Copiamos el archivo de requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código principal de la aplicación
# Asumimos que app.py está en el root de tu proyecto
COPY app.py .

# Crear el directorio de uploads que se usará para el LFI.
# Esto es redundante si usas el volumen, pero asegura que el directorio existe.
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Exponer el puerto de la aplicación
EXPOSE 8080

# Comando de ejecución
CMD ["python", "app.py"]
