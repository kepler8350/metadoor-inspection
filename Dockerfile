FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir Flask==2.3.2

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
