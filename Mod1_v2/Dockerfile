FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ВАЖНО: добираем зависимости для ctranslate2/onnxruntime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgomp1 \
    libopenblas0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app/requirements.txt /app/app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY . /app

ENV DB_URL="sqlite:////app/data/asr.db"

EXPOSE 8080
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]