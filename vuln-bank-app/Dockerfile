# Usa una versión de Python estable y ligera
FROM python:3.9-slim

# Nota: El usuario root es intencional para las pruebas de escalada de privilegios y CMDi.
USER root

# Instalación de herramientas de prueba y dependencias de la aplicación
RUN apt-get update && apt-get install -y \
    net-tools \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Definimos el directorio de trabajo (donde se ejecutará la aplicación)
WORKDIR /app

# Copiamos el archivo de requisitos (asumiendo que está en la raíz del proyecto)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos toda la carpeta 'app' (que contiene el código, incluyendo app.py)
# Esto mapea ./app/ -> /app/ dentro del contenedor.
COPY app/ .

# Crear el directorio de uploads que se usará para el LFI/Path Traversal.
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Exponer el puerto de la aplicación
EXPOSE 8080

# Comando de ejecución: Lanza app.py desde el directorio de trabajo /app
CMD ["python", "app.py"]
