# CoffeeMap PWA 배포 가이드

## 🚀 배포 단계

### 1. 백엔드 배포 (Railway)

1. **Railway 가입**
   - https://railway.app 접속
   - GitHub 계정으로 로그인

2. **프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - `LemonLucy/cafemap` 저장소 선택
   - `main` 브랜치 선택

3. **환경 변수 설정**
   - Settings → Variables 클릭
   - 추가:
     ```
     NAVER_CLIENT_ID=tr30Ch1tbJBqwNlv9svx
     NAVER_CLIENT_SECRET=fsrn1wXmk3
     ```

4. **배포 URL 복사**
   - 예: `https://your-app.railway.app`

### 2. 프론트엔드 배포 (Vercel)

1. **Vercel 가입**
   - https://vercel.com 접속
   - GitHub 계정으로 로그인

2. **프로젝트 Import**
   - "Add New" → "Project" 클릭
   - `LemonLucy/cafemap` 저장소 선택
   - Root Directory: `coffeemap` 선택

3. **환경 변수 설정**
   - Environment Variables 섹션에서:
     ```
     BACKEND_URL=https://your-app.railway.app
     ```

4. **배포**
   - "Deploy" 클릭
   - 자동 배포 완료 (2-3분)

5. **배포 URL 확인**
   - 예: `https://coffeemap.vercel.app`

### 3. 백엔드 URL 업데이트

배포 후 `index.html`에서 백엔드 URL 수정:

```javascript
// 현재
const API_BASE_URL = 'http://localhost:5000';

// 변경
const API_BASE_URL = 'https://your-app.railway.app';
```

Git 커밋 후 자동 재배포됨.

### 4. PWA 설치 테스트

**아이폰:**
1. Safari에서 `https://coffeemap.vercel.app` 접속
2. 공유 버튼 → "홈 화면에 추가"
3. 앱 아이콘 생성됨

**Android:**
1. Chrome에서 접속
2. "홈 화면에 추가" 팝업 클릭
3. 앱 아이콘 생성됨

## 📱 배포 완료 후

- ✅ HTTPS 자동 적용
- ✅ 전 세계 CDN 배포
- ✅ 자동 SSL 인증서
- ✅ Git push 시 자동 재배포
- ✅ 무료 (Railway 월 $5 크레딧, Vercel 무료)

## 🔧 문제 해결

**CORS 에러:**
`app_server.py`에 이미 CORS 설정 있음:
```python
self.send_header('Access-Control-Allow-Origin', '*')
```

**캐시 문제:**
브라우저에서 `localStorage.clear()` 실행

## 📊 모니터링

- Railway: 로그 및 메트릭 확인
- Vercel: Analytics 및 배포 로그

## 💰 비용

- **Railway**: 월 $5 크레딧 (무료)
- **Vercel**: 무료 (Hobby 플랜)
- **총**: 무료!
