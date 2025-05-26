# 1. Usar una imagen base oficial de Python
# Usaremos una versión "slim" para que la imagen sea más ligera.
# Asegúrate de que esta versión de Python sea compatible con tu código.
# Python 3.9 es una buena opción general, pero puedes ajustarla.
FROM python:3.9-slim-bullseye

# 2. Establecer el directorio de trabajo dentro del contenedor
# Aquí es donde copiaremos nuestro código y ejecutaremos los comandos.
WORKDIR /app

# 3. Copiar el archivo de requerimientos primero
# Esto aprovecha el caché de capas de Docker: si requirements.txt no cambia,
# Docker no reinstalará las dependencias en cada build (si solo cambia el código .py).
COPY requirements.txt .

# 4. Instalar las dependencias listadas en requirements.txt
# --no-cache-dir reduce el tamaño de la imagen al no guardar el caché de pip.
# --trusted-host pypi.python.org -U pip setuptools # Opcional: actualiza pip y setuptools, a veces útil.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código de la aplicación al directorio de trabajo
# El primer '.' se refiere al directorio actual de nuestro proyecto (el contexto de build).
# El segundo '.' se refiere al WORKDIR (/app) dentro del contenedor.
COPY . .
# Si solo quieres copiar scraper.py: COPY scraper.py .

# 6. (Opcional pero recomendado) Crear un directorio para la salida de datos dentro del contenedor
RUN mkdir -p /app/output 
# El script Python guardará el CSV aquí dentro del contenedor.

# 7. Comando para ejecutar la aplicación cuando se inicie el contenedor
# Esta es la forma "exec", que es la preferida para CMD.
CMD ["python", "scraper.py"]