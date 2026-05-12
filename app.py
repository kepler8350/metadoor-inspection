from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head><title>메타도어</title></head>
<body>
<h1>메타도어 점검 시스템</h1>
<p>✓ 성공!</p>
</body>
</html>'''

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    # 표준출력에 포트 정보 출력
    print('Starting Flask app...', file=sys.stderr, flush=True)
    app.run(host='0.0.0.0', port=8080)
