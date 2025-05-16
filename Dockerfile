FROM python:3.11-slim

WORKDIR /app

# Copiar TODOS los archivos necesarios
COPY requirements.txt .
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Configurar PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["sh", "-c", "python database/load_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]