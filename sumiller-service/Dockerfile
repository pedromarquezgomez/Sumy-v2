# Usa una imagen oficial de Python ligera y segura.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Crear un usuario no-root para mayor seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copia solo el archivo de requisitos para aprovechar el caché de capas de Docker.
COPY --chown=app:app requirements.txt .

# Instala las dependencias de Python.
RUN pip install --user --no-cache-dir -r requirements.txt

# Asegurar que los binarios de pip estén en el PATH
ENV PATH="/home/app/.local/bin:${PATH}"

# Copia el resto del código de la aplicación.
COPY --chown=app:app . .

# Cloud Run inyecta PORT como variable de entorno
ENV PORT=8080

# Expone el puerto en el que se ejecutará la aplicación.
EXPOSE $PORT

# El comando por defecto para iniciar la aplicación.
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
