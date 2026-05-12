FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir Flask==2.3.2

COPY app.py .

# Railway에서 사용할 환경변수
ENV PORT=5000

# 컨테이너 포트 노출
EXPOSE 5000

# Flask 앱 실행
CMD ["python", "app.py"]
