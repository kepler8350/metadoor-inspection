from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 50px 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
            animation: slideIn 0.6s ease-out;
        }
        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .icon { font-size: 100px; margin-bottom: 20px; animation: bounce 2s infinite; }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        h1 { color: #333; margin-bottom: 15px; font-size: 36px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 16px; }
        .message {
            color: #27ae60;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            background: #f0fdf4;
            border-radius: 10px;
            border-left: 5px solid #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🏛️</div>
        <h1>메타도어</h1>
        <p class="subtitle">유지보수 점검 시스템</p>
        <div class="message">✓ 성공적으로 배포되었습니다!</div>
    </div>
</body>
</html>"""
    return html_content

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
