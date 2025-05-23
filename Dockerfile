FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 8000
ENV DATABASE_URL=${DATABASE_URL}
ENV RENDER=${RENDER}

CMD ["sh", "-c", "\
    python database/load_data.py && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} \
"]
