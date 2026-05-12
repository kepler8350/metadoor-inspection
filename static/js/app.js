// 전역 상태
const state = {
    isLoggedIn: false,
    userId: '',
    selectedDistrict: '',
    currentSignature: null
};

// 화면 전환 함수
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

// 로그인 처리
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userId = document.getElementById('userId').value;
    const password = document.getElementById('userPassword').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ userId, password })
        });
        
        if (response.ok) {
            state.isLoggedIn = true;
            state.userId = userId;
            await loadDistricts();
            showScreen('selectDistrictScreen');
        } else {
            alert('로그인 실패: 아이디 또는 비밀번호를 확인하세요.');
        }
    } catch (error) {
        alert('로그인 중 오류가 발생했습니다: ' + error.message);
    }
});

// 구 목록 로드
async function loadDistricts() {
    try {
        const response = await fetch('/api/districts');
        const data = await response.json();
        
        const districtList = document.getElementById('districtList');
        districtList.innerHTML = '';
        
        data.districts.forEach(district => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'district-button';
            button.textContent = district;
            button.onclick = () => selectDistrict(district);
            districtList.appendChild(button);
        });
    } catch (error) {
        alert('구 목록 로드 중 오류: ' + error.message);
    }
}

// 구 선택
function selectDistrict(district) {
    state.selectedDistrict = district;
    document.getElementById('selectedDistrict').textContent = district;
    clearSignature();
    showScreen('inspectionScreen');
}

// 서명 캔버스 초기화
const canvas = document.getElementById('signatureCanvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;

canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;
    const rect = canvas.getBoundingClientRect();
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#333';
});

canvas.addEventListener('mouseup', () => {
    isDrawing = false;
});

canvas.addEventListener('mouseleave', () => {
    isDrawing = false;
});

// 터치 이벤트 지원 (모바일)
canvas.addEventListener('touchstart', (e) => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    ctx.beginPath();
    ctx.moveTo(touch.clientX - rect.left, touch.clientY - rect.top);
});

canvas.addEventListener('touchmove', (e) => {
    if (!isDrawing) return;
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    ctx.lineTo(touch.clientX - rect.left, touch.clientY - rect.top);
    ctx.stroke();
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#333';
});

canvas.addEventListener('touchend', () => {
    isDrawing = false;
});

// 서명 지우기
function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    state.currentSignature = null;
}

// 점검 데이터 저장
async function saveInspection() {
    const inspectionItem = document.getElementById('inspectionItem').value;
    const actionDetail = document.getElementById('actionDetail').value;
    
    if (!inspectionItem) {
        alert('점검 항목을 선택해주세요.');
        return;
    }
    
    if (!actionDetail.trim()) {
        alert('조치 내용을 입력해주세요.');
        return;
    }
    
    // 서명 이미지로 변환
    const signatureImage = canvas.toDataURL('image/png');
    
    try {
        const response = await fetch('/api/inspection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                district: state.selectedDistrict,
                inspectionItem: inspectionItem,
                locationDetail: document.getElementById('actionDetail').value,
                action: actionDetail,
                signature: signatureImage
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            document.getElementById('completeDetails').textContent = 
                `점검 ID: ${result.inspection_id}\n지역: ${state.selectedDistrict}`;
            showScreen('completeScreen');
        } else {
            alert('저장 중 오류가 발생했습니다.');
        }
    } catch (error) {
        alert('저장 중 오류: ' + error.message);
    }
}

// 뒤로 가기
function goBack() {
    const activeScreen = document.querySelector('.screen.active').id;
    
    if (activeScreen === 'inspectionScreen') {
        showScreen('selectDistrictScreen');
    } else if (activeScreen === 'selectDistrictScreen') {
        logout();
    }
}

// 처음으로
function goToHome() {
    showScreen('selectDistrictScreen');
    clearSignature();
    document.getElementById('inspectionForm').reset();
}

// 로그아웃
async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        state.isLoggedIn = false;
        state.userId = '';
        state.selectedDistrict = '';
        document.getElementById('loginForm').reset();
        showScreen('loginScreen');
    } catch (error) {
        alert('로그아웃 중 오류: ' + error.message);
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    showScreen('loginScreen');
});
