FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir Flask==2.3.2

COPY app.py .

ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "python app.py"]
