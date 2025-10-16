# 로그 시스템 설정 및 사용 가이드

## 📋 구현 완료 항목

### ✅ 1. Docker Compose로 Elasticsearch 환경 구성
- `docker-compose.yml`: Elasticsearch + Kibana 설정
- Elasticsearch 8.11.0, Kibana 8.11.0
- 개발환경용 설정 (보안 비활성화)

### ✅ 2. 로그 스키마 및 모델 정의
- `app/schemas/log.py`: 로그 데이터 모델
- `PIIDetectionLog`: 탐지 로그 스키마
- `LogSearchRequest/Response`: 검색 요청/응답 스키마
- `LogStatsResponse`: 통계 응답 스키마

### ✅ 3. Repository 구현
- `app/repositories/log_repository.py`: Elasticsearch 저장소
- 로그 저장/조회/통계 기능
- 싱글톤 패턴으로 인스턴스 관리

### ✅ 4. PII 탐지 시 로그 남기기
- `app/services/pii_service.py`: 로깅 기능 통합
- 클라이언트 IP, User-Agent, 처리시간 등 자동 수집
- 탐지 결과 상세 정보 저장

### ✅ 5. 로그 조회 API
- `app/api/routers/logs.py`: 로그 관리 API
- `app/services/log_service.py`: 로그 서비스
- 검색, 통계, 최근 로그 조회 기능

## 🚀 실행 방법

### 1. Elasticsearch 환경 시작
```bash
# Docker Compose로 Elasticsearch 시작
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 2. 의존성 설치
```bash
# 새로운 Elasticsearch 의존성 설치
uv sync
```

### 3. 서버 실행
```bash
# FastAPI 서버 시작
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 서비스 확인
```bash
# Elasticsearch 상태 확인
curl http://localhost:9200/_cluster/health

# Kibana 접속 (선택사항)
# http://localhost:5601

# API 문서 확인
# http://localhost:8000/docs
```

## 📡 API 사용법

### 1. PII 탐지 (로그 자동 저장)
```bash
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"}'
```

### 2. 로그 검색
```bash
# 최근 24시간 로그 조회
curl "http://localhost:8000/api/v1/logs/search"

# PII 탐지된 로그만 조회
curl "http://localhost:8000/api/v1/logs/search?has_pii=true"

# 특정 IP의 로그 조회
curl "http://localhost:8000/api/v1/logs/search?client_ip=192.168.1.100"

# 엔티티 타입별 필터링
curl "http://localhost:8000/api/v1/logs/search?entity_types=PERSON,PHONE"

# 텍스트 검색
curl "http://localhost:8000/api/v1/logs/search?search_text=홍길동"
```

### 3. 로그 통계
```bash
# 최근 7일 통계
curl "http://localhost:8000/api/v1/logs/stats"

# 최근 30일 통계
curl "http://localhost:8000/api/v1/logs/stats?days=30"
```

### 4. 최근 로그
```bash
# 최근 24시간 로그 (최대 50개)
curl "http://localhost:8000/api/v1/logs/recent"

# 최근 로그 100개
curl "http://localhost:8000/api/v1/logs/recent?limit=100"
```

### 5. 서비스 상태 확인
```bash
# PII 탐지 서비스 상태
curl "http://localhost:8000/api/v1/pii/health"

# 로그 서비스 상태
curl "http://localhost:8000/api/v1/logs/health"
```

## 📊 로그 데이터 구조

### 저장되는 정보
- **기본 정보**: ID, 타임스탬프, 로그 레벨
- **요청 정보**: 클라이언트 IP, User-Agent, Request ID
- **PII 탐지 결과**: 입력 텍스트, 탐지 여부, 엔티티 정보
- **처리 정보**: 처리 시간, 모델 신뢰도
- **응답 정보**: 탐지 이유, 상세 설명
- **메타데이터**: 서비스 버전, 모델 정보

### 엔티티 정보
- **type**: PERSON, PHONE, EMAIL 등
- **value**: 탐지된 실제 값
- **confidence**: 탐지 신뢰도 (0.0 ~ 1.0)
- **token_count**: 토큰 개수

## 🔍 Elasticsearch 인덱스 구조

### 인덱스명: `ai-tls-dlp-logs`
```json
{
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "client_ip": {"type": "ip"},
      "input_text": {"type": "text", "analyzer": "korean"},
      "has_pii": {"type": "boolean"},
      "entity_types": {"type": "keyword"},
      "processing_time_ms": {"type": "float"},
      "detected_entities": {
        "type": "nested",
        "properties": {
          "type": {"type": "keyword"},
          "value": {"type": "text"},
          "confidence": {"type": "float"}
        }
      }
    }
  }
}
```

## 🛠️ 환경 변수 설정

```bash
# Elasticsearch 설정
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX_PREFIX=ai-tls-dlp
LOG_TO_ELASTICSEARCH=true
LOG_RETENTION_DAYS=30
```

## 📈 모니터링 및 분석

### Kibana 대시보드 (선택사항)
1. http://localhost:5601 접속
2. 인덱스 패턴 생성: `ai-tls-dlp-logs*`
3. 대시보드 생성으로 시각화

### API 통계 조회
- 실시간 PII 탐지율 모니터링
- 시간대별 요청 패턴 분석
- 엔티티 타입별 탐지 현황
- 상위 IP 주소 모니터링

## 🔧 문제 해결

### Elasticsearch 연결 실패
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs elasticsearch

# 컨테이너 재시작
docker-compose restart elasticsearch
```

### 로그 저장 실패
- `LOG_TO_ELASTICSEARCH=false`로 설정하여 비활성화 가능
- 서비스는 정상 동작하되 로그만 저장되지 않음

### 성능 최적화
- Elasticsearch 메모리 설정 조정
- 로그 보관 기간 설정 (`LOG_RETENTION_DAYS`)
- 인덱스 샤드/레플리카 설정 조정

## 🎯 완성된 기능

1. **자동 로깅**: PII 탐지 시 모든 정보가 자동으로 Elasticsearch에 저장
2. **다양한 검색**: IP, 시간, 엔티티 타입, 텍스트 내용으로 검색 가능
3. **통계 분석**: 탐지율, 처리시간, 시간대별 패턴 등 상세 통계
4. **실시간 모니터링**: 최근 로그 조회 및 서비스 상태 확인
5. **확장 가능**: 향후 알림, 대시보드 등 추가 기능 확장 용이

이제 완전한 로그 시스템이 구축되어 PII 탐지 활동을 체계적으로 모니터링할 수 있습니다! 🚀
