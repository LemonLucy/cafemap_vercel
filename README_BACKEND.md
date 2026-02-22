# CoffeeMap Backend

카공 최적화 카페 찾기 - 백엔드 API 서버

## 배포

### Railway 배포

1. [Railway](https://railway.app) 가입
2. "New Project" → "Deploy from GitHub repo"
3. 이 저장소 선택
4. 환경 변수 설정:
   - `NAVER_CLIENT_ID`: tr30Ch1tbJBqwNlv9svx
   - `NAVER_CLIENT_SECRET`: fsrn1wXmk3
5. 자동 배포 완료

### 로컬 실행

```bash
bash START_SERVERS.sh
```

## API 엔드포인트

- `POST /api/blog-search` - 카페 블로그 분석
- `POST /api/clear-cache` - 캐시 초기화

## 환경 변수

```
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```
