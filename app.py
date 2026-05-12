from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>메타도어</title>
    </head>
    <body>
        <h1>메타도어 점검 시스템</h1>
        <p>✓ 성공적으로 배포되었습니다!</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return 'OK'
