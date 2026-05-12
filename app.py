from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>메타도어 점검</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .login-card {
                background: white;
                border-radius: 20px;
                padding: 40px;
                width: 100%;
                max-width: 420px;
                text-align: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }
            .app-icon { font-size: 60px; margin-bottom: 15px; }
            h1 { font-size: 28px; color: #1e3c72; margin: 0 0 5px; }
            .subtitle { color: #666; font-size: 14px; margin-bottom: 30px; }
            .form-group { display: flex; flex-direction: column; gap: 16px; }
            label { text-align: left; font-size: 13px; font-weight: 500; color: #333; }
            input {
                width: 100%;
                padding: 12px 14px;
                border: 0.5px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
                background: #fafafa;
                font-family: inherit;
            }
            button {
                padding: 14px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                margin-top: 8px;
                transition: transform 0.2s;
            }
            button:hover { transform: scale(0.98); }
            .help { color: #999; font-size: 13px; margin-top: 8px; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="app-icon">🏛️</div>
            <h1>메타도어</h1>
            <p class="subtitle">유지보수 점검 시스템</p>
            
            <form class="form-group" onsubmit="login(event)">
                <div>
                    <label>아이디</label>
                    <input type="text" id="userId" placeholder="아이디" value="test" required>
                </div>
                <div>
                    <label>비밀번호</label>
                    <input type="password" id="password" placeholder="비밀번호" value="test" required>
                </div>
                <button type="submit">로그인</button>
                <p class="help">권한자가 등록한 직원만 로그인할 수 있습니다.</p>
            </form>
        </div>

        <script>
        function login(e) {
            e.preventDefault();
            var userId = document.getElementById('userId').value;
            var password = document.getElementById('password').value;
            
            if (userId === 'test' && password === 'test') {
                alert('로그인 성공!\\n다음 화면: 부산 구 선택');
            } else {
                alert('아이디 또는 비밀번호가 올바르지 않습니다.');
            }
        }
        </script>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'MetaDoor is running'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
