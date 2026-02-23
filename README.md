# CoffeeMap

카카오 맵 기반 카페 검색 및 블로그 리뷰 분석 서비스

## 실행 방법

```bash
bash START_SERVERS.sh
```

브라우저에서 http://localhost:8000 접속

## 주요 기능

- 카카오 맵 기반 카페 검색
- 네이버 블로그 리뷰 자동 수집
- 블로그 이미지 다운로드
- 작업 환경 분석 (콘센트, 작업 적합도)
- 카페 테마 분석 (Cat Cafe, Dog Cafe, Book Cafe 등)

## 파일 구조

- `index.html` - 프론트엔드 (카카오 맵 UI)
- `app_server.py` - 백엔드 서버 (포트 5000)
- `config.js` - 카카오 API 키 설정
- `database.py` - SQLite 데이터베이스
- `test_server/` - 네이버 블로그 크롤링 모듈
- `static/cafe_images/` - 다운로드된 카페 이미지

## API 키 설정

`.env` 파일:
```
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

`config.js` 파일:
```javascript
const CONFIG = {
    KAKAO_API_KEY: 'your_kakao_key'
};
```

## 서버 관리

- 시작: `bash START_SERVERS.sh`
- 중지: `pkill -f app_server.py`
- 로그: `tail -f server.log`
# CafeMap
