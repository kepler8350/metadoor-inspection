import os
import sys
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>메타도어 점검</title>
    </head>
    <body style="text-align: center; padding: 50px; font-family: Arial;">
        <h1>🏛️ 메타도어</h1>
        <p>유지보수 점검 시스템</p>
        <p style="color: green; font-size: 20px;">✓ 성공적으로 배포되었습니다!</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f'Flask would run on port {port}', file=sys.stderr, flush=True)
