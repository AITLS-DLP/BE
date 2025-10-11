# AI-TLS-DLP Backend v1.0.0

## 프로젝트 개요

한국어 개인정보(PII) 탐지를 위한 **정규식 + BERT NER** 기반 FastAPI 백엔드 서비스입니다.

허깅페이스의 `psh3333/roberta-large-korean-pii5` 모델을 사용하여 실시간 PII 탐지 및 차단 기능을 제공합니다.

## ✨ 주요 기능 (v1.0.0)

- ✅ **정규식 기반 PII 탐지**: 전화번호, 이메일 등 패턴 매칭
- ✅ **BERT NER 기반 PII 탐지**: RoBERTa 모델을 활용한 개인정보 엔티티 인식
- ✅ **실시간 차단 판단**: 탐지된 PII 기반 자동 차단 여부 결정
- ✅ **RESTful API**: FastAPI 기반 고성능 API
- ✅ **자동 문서화**: Swagger UI 제공

## 🏗️ 프로젝트 구조

```
DLP-BE/
├── app/
│   ├── main.py              # FastAPI 진입점
│   ├── api/routers/
│   │   └── pii.py          # PII 탐지 API
│   ├── services/
│   │   └── pii_service.py  # 비즈니스 로직
│   ├── ai/
│   │   ├── pii_detector.py # RoBERTa PII 탐지 모델
│   │   └── model_manager.py # 모델 싱글톤 관리
│   ├── schemas/
│   │   └── pii.py          # Request/Response 스키마
│   ├── utils/
│   │   └── entity_extractor.py # BIO 태그 엔티티 추출
│   └── core/
│       └── config.py       # 설정
├── pyproject.toml           # 의존성 관리
└── CLAUDE.md                # 개발 문서
```

## 🚀 빠른 시작

### 1. 요구사항

- Python 3.13+
- uv (또는 pip)

### 2. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

### 3. 서버 실행

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API 사용법

### PII 탐지

**엔드포인트**: `POST /api/v1/pii/detect`

**요청 예시**:
```bash
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"}'
```

**응답 예시**:
```json
{
  "has_pii": true,
  "reason": "개인정보 2개 탐지됨 (PERSON, PHONE_NUM)",
  "details": "탐지된 개인정보: PERSON '홍길동' (신뢰도: 95.0%), PHONE_NUM '010-1234-5678' (신뢰도: 89.0%)",
  "entities": [
    {
      "type": "PERSON",
      "value": "홍길동",
      "confidence": 0.95,
      "token_count": 2
    },
    {
      "type": "PHONE_NUM",
      "value": "010-1234-5678",
      "confidence": 0.89,
      "token_count": 7
    }
  ]
}
```

### 헬스체크

**엔드포인트**: `GET /api/v1/pii/health`

```bash
curl -X GET "http://localhost:8000/api/v1/pii/health"
```

## 🛠️ 기술 스택

- **백엔드**: FastAPI + Python 3.13
- **AI 모델**: Transformers + PyTorch
- **PII 모델**: `psh3333/roberta-large-korean-pii5`
- **패키지 관리**: uv

## 📊 성능

- **첫 요청**: ~2초 (모델 로딩 포함)
- **이후 요청**: 100-300ms
- **처리 가능 텍스트**: 최대 512 토큰 (약 1000자)

## 🗺️ 로드맵

### Phase 1: 기본 PII 탐지 (완료) ✅
- RoBERTa 모델 통합
- 정규식 기반 패턴 매칭
- BIO 태깅 정확도 개선
- 모델 성능 최적화

### Phase 2: 확장 기능 (예정)
- 문서 업로드 및 파싱 (PDF, DOCX)
- 유사도 기반 문서 비교 (KoSimCSE)
- 벡터 DB 연동 (ChromaDB)
- 데이터베이스 통합 (PostgreSQL)

### Phase 3: 운영 준비 (예정)
- 단위/통합 테스트
- 로깅 및 모니터링
- Rate limiting 및 보안 강화
- Docker 컨테이너화

## 📝 환경 변수 설정

`.env` 파일 생성 (선택사항):

```bash
# AI 모델 설정
PII_MODEL_NAME=psh3333/roberta-large-korean-pii5

# 분석 설정
DEFAULT_PII_THRESHOLD=0.59

# 모델 모드
MODEL_MODE=LOCAL
```

## 🧪 테스트

```bash
# 간단한 테스트
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "홍길동의 연락처는 010-1234-5678입니다"}'
```

## 📖 문서

자세한 개발 문서는 [CLAUDE.md](./CLAUDE.md)를 참고하세요.

## 🤝 기여

이 프로젝트는 KISIA 프로젝트의 일부입니다.

## 📄 라이선스

이 프로젝트의 라이선스는 프로젝트 소유자와 협의하세요.

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.

---

**AI-TLS-DLP Backend v1.0.0** - 정규식 + BERT NER 기반 PII 탐지 시스템