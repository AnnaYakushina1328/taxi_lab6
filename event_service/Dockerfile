FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rabbitmq_client.py .
COPY producer.py .
COPY consumer.py .
COPY test_events.py .

CMD ["python", "consumer.py"]
