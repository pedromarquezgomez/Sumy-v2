# Usa una imagen oficial de Python ligera y segura.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia solo el archivo de requisitos para aprovechar el caché de capas de Docker.
COPY requirements.txt .

# Instala las dependencias de Python.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación.
COPY . .

# Expone el puerto en el que se ejecutará la aplicación.
EXPOSE 8080

# El comando por defecto para iniciar la aplicación.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
