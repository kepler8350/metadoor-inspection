from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'MetaDoor is running!'

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    # Railway에서는 포트 8080을 사용하므로 이를 기본값으로 설정
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
