# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# 1. Copia e instala dependencias lo antes posible
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia el resto del código
COPY . .

# 3. Asegura que Python pueda importar tu paquete
ENV PYTHONPATH="${PYTHONPATH}:/app"

# 4. Documenta el puerto interno por defecto
EXPOSE 8000
ENV DATABASE_URL=${DATABASE_URL}
ENV RENDER=${RENDER}

CMD ["sh", "-c", "\
    python database/load_data.py && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} \
"]
