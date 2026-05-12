from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        h1 { color: #333; margin-bottom: 20px; }
        .icon { font-size: 80px; margin-bottom: 20px; }
        .message { color: green; font-size: 24px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🏛️</div>
        <h1>메타도어</h1>
        <p style="color: #666; margin-bottom: 30px;">유지보수 점검 시스템</p>
        <div class="message">✓ 성공적으로 배포되었습니다!</div>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    print('=' * 50, file=sys.stderr, flush=True)
    print('Flask app starting on 0.0.0.0:8080', file=sys.stderr, flush=True)
    print('=' * 50, file=sys.stderr, flush=True)
    app.run(host='0.0.0.0', port=8080, debug=False)
