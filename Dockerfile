FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Polling bot — HTTP port yo'q. Koyeb'da "Worker" turi sifatida ishga tushiring.
CMD ["python", "main.py"]
