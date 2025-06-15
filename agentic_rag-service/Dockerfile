FROM python:3.11-slim

WORKDIR /app

# Crear un usuario no-root para mayor seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

COPY --chown=app:app requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Asegurar que los binarios de pip estén en el PATH
ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app . .

# Cloud Run inyecta PORT como variable de entorno
ENV PORT=8080

EXPOSE $PORT

CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
