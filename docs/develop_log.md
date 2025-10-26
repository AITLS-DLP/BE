# 개발 로그 (Development Log)

이 문서는 프로젝트의 모든 개발 및 수정 이력을 기록합니다.

---

## 2025-10-21: 대시보드 '오늘 차단횟수' 시간대 문제 해결 및 기능 고도화

### 요약
대시보드에 '오늘 차단횟수'가 0으로 표시되는 문제를 해결하고, 시간대를 동적으로 처리하도록 백엔드와 프론트엔드 기능을 모두 개선했습니다. API 계약(Contract)을 명확히 하여 안정성을 높였습니다.

### 원인 분석
- API는 200 OK를 반환하지만 값이 0으로 집계되는 현상 확인.
- **가설 A(시간대 불일치)** 채택: 백엔드가 UTC 기준으로 ‘오늘’을 집계하는 반면, 실제 데이터는 KST 기준으로 생성되어 발생한 문제로 판단.

### 백엔드 변경 사항
1.  **API 라우터 수정 (`api/routers/metrics.py`)**:
    *   `GET /blocks/today` 엔드포인트가 클라이언트의 시간대를 나타내는 `tz` 쿼리 파라미터를 받도록 수정했습니다. (기본값: "UTC")
    *   유효하지 않은 시간대 입력 시 400 에러를 반환하는 검증 로직을 추가했습니다.
2.  **유스케이스 로직 변경 (`usecases/metrics_usecases.py`)**:
    *   `GetTodayBlockCountUseCase`가 `tz`를 인자로 받아, 해당 시간대 기준으로 ‘오늘’의 시작 시각을 동적으로 계산하도록 로직을 변경했습니다.
3.  **API 스키마 확정 (`schemas/metrics.py`)**:
    *   `TodayBlockCountResponse` 스키마를 `{count, start_of_day, timezone}`으로 변경하여 API 계약을 명확히 했습니다.

### 프론트엔드 변경 사항
1.  **커스텀 훅 수정 (`hooks/useDashboardMetrics.js`)**:
    *   `Intl.DateTimeFormat().resolvedOptions().timeZone`을 사용하여 브라우저의 시간대를 자동으로 감지합니다.
    *   API 호출 시 감지된 시간대를 `tz` 쿼리 파라미터로 함께 전송합니다.
    *   새로운 API 응답 스키마(`{count: number}`)에 맞춰 데이터를 안전하게 파싱하도록 수정했습니다. (`data?.count ?? 0`)
2.  **UI 컴포넌트 개선 (`app/dashboard/command-center/page.jsx`)**:
    *   데이터를 기다리는 중일 때 `...` (로딩), API 호출 실패 시 `오류` (에러), 데이터가 0건일 때 `0`이 명확하게 표시되도록 UI를 개선했습니다.

### 최종 API 계약
- **Endpoint**: `GET /api/v1/metrics/blocks/today?tz={IANA_Timezone}`
- **Response**: 
  ```json
  {
    "count": 123,
    "start_of_day": "2025-10-21T00:00:00+09:00",
    "timezone": "Asia/Seoul"
  }
  ```

---

## 2025-10-20: 대시보드 '오늘 차단횟수' 위젯 기능 구현

### 요약
대시보드의 '오늘 차단횟수' 위젯에 실제 데이터를 연동하기 위해 백엔드 API부터 프론트엔드 컴포넌트까지 전체 스택을 구현했습니다.

### 백엔드 변경 사항
- **신규 API 생성**: `GET /api/v1/metrics/blocks/today` 엔드포인트를 생성하여 오늘의 총 차단 횟수를 제공합니다.
- **아키텍처 확장**:
    - `app/api/routers/metrics.py`: 통계 관련 API 라우터 신규 생성.
    - `app/usecases/metrics_usecases.py`: `GetTodayBlockCountUseCase`를 정의하여 비즈니스 흐름 관리.
    - `app/schemas/metrics.py`: `TodayBlockCountResponse` 응답 스키마 정의.
- **서비스/리포지토리 계층 수정**:
    - `app/repositories/log_repository.py`: Elasticsearch `count` 쿼리를 사용하여 특정 시간 이후의 차단 로그(가설: `metadata.action: "BLOCK"`)를 집계하는 `count_blocks_since` 메소드를 추가했습니다.
    - `app/services/log_service.py`: 리포지토리 메소드를 호출하는 `get_block_count_since` 서비스 메소드를 추가했습니다.
- **라우터 등록**: `app/main.py`에 신규 `metrics_router`를 등록하여 API를 활성화했습니다.

### 프론트엔드 변경 사항
- **커스텀 Hook 생성**: `hooks/useDashboardMetrics.js`를 생성하여 `/api/v1/metrics/blocks/today` API 호출 및 상태(loading, error, data) 관리 로직을 캡슐화했습니다.
- **컴포넌트 연동**: `app/dashboard/command-center/page.jsx`에서 `useDashboardMetrics` 훅을 사용하여, 기존의 정적 데이터를 API로부터 받아온 동적 데이터로 교체했습니다. 로딩 및 에러 상태에 따른 UI 처리 로직도 추가했습니다.
- **API 라이브러리 보강**: `lib/api.js`에 향후 로그인 기능 구현에 필요한 `post` 메소드를 미리 추가하여 확장성을 확보했습니다.

### 후속 조치
- Elasticsearch에 '차단' 로그가 어떤 필드/값으로 저장되는지에 대한 가설(`metadata.action: "BLOCK"`)이 올바른지 실제 데이터 확인 필요.

---

## 2025-10-20: 대시보드 '오늘 차단횟수' 위젯 기능 구현

### 요약
대시보드의 '오늘 차단횟수' 위젯에 실제 데이터를 연동하기 위해 백엔드 API부터 프론트엔드 컴포넌트까지 전체 스택을 구현했습니다.

### 백엔드 변경 사항
- **신규 API 생성**: `GET /api/v1/metrics/blocks/today` 엔드포인트를 생성하여 오늘의 총 차단 횟수를 제공합니다.
- **아키텍처 확장**:
    - `app/api/routers/metrics.py`: 통계 관련 API 라우터 신규 생성.
    - `app/usecases/metrics_usecases.py`: `GetTodayBlockCountUseCase`를 정의하여 비즈니스 흐름 관리.
    - `app/schemas/metrics.py`: `TodayBlockCountResponse` 응답 스키마 정의.
- **서비스/리포지토리 계층 수정**:
    - `app/repositories/log_repository.py`: Elasticsearch `count` 쿼리를 사용하여 특정 시간 이후의 차단 로그(가설: `metadata.action: "BLOCK"`)를 집계하는 `count_blocks_since` 메소드를 추가했습니다.
    - `app/services/log_service.py`: 리포지토리 메소드를 호출하는 `get_block_count_since` 서비스 메소드를 추가했습니다.
- **라우터 등록**: `app/main.py`에 신규 `metrics_router`를 등록하여 API를 활성화했습니다.

### 프론트엔드 변경 사항
- **커스텀 Hook 생성**: `hooks/useDashboardMetrics.js`를 생성하여 `/api/v1/metrics/blocks/today` API 호출 및 상태(loading, error, data) 관리 로직을 캡슐화했습니다.
- **컴포넌트 연동**: `app/dashboard/command-center/page.jsx`에서 `useDashboardMetrics` 훅을 사용하여, 기존의 정적 데이터를 API로부터 받아온 동적 데이터로 교체했습니다. 로딩 및 에러 상태에 따른 UI 처리 로직도 추가했습니다.
- **API 라이브러리 보강**: `lib/api.js`에 향후 로그인 기능 구현에 필요한 `post` 메소드를 미리 추가하여 확장성을 확보했습니다.

### 후속 조치
- Elasticsearch에 '차단' 로그가 어떤 필드/값으로 저장되는지에 대한 가설(`metadata.action: "BLOCK"`)이 올바른지 실제 데이터 확인 필요.

---

## 2025-10-16: 프론트엔드 아키텍처 가이드라인 수립

### 요약

프론트엔드(`Admin-FE`) 프로젝트의 일관성 있는 개발을 위해 클린 아키텍처 가이드라인을 정립하고 `GEMINI.md`에 문서화함.

### 주요 변경 사항

*   **파일**: `docs/GEMINI.md`
*   **내용**: 프론트엔드 아키텍처 섹션을 신규 추가함.
*   **아키텍처 정의**: `Page/Layout → Hook → Service → (API)`의 계층 구조를 정의하고, 각 계층(폴더)의 역할과 책임을 명확히 함.
    *   `app/`: 라우팅 및 페이지 최상위 계층
    *   `components/`: 재사용 가능한 "Dumb" UI 컴포넌트
    *   `hooks/`: 재사용 가능한 상태 관련 로직 (API 호출, 폼 관리 등)
    *   `contexts/`: 전역 상태 관리
    *   `lib/` 또는 `services/`: 외부 API 통신 및 순수 유틸리티 함수

### 기대 효과

*   백엔드와 마찬가지로 프론트엔드에서도 역할과 책임이 명확히 분리된 구조를 유지하여, 유지보수 및 기능 확장의 효율성을 증대시킴.

---

## 2025-10-16: "AI 탐지 정책 설정" 백엔드 기능 구현

### 요약

기능 명세서(ID: FE-005, BE-004)에 따라 "AI 탐지 정책 설정" 기능의 백엔드 API를 신규 구현함. 프론트엔드에서 탐지 규칙 목록을 조회하고, 각 규칙의 활성화 상태를 변경할 수 있는 기능을 제공함.

### 주요 변경 사항

1.  **데이터베이스 모델 추가**:
    *   `app/models/detection_rule.py` 파일을 생성하고, `detection_rules` 테이블에 매핑될 `DetectionRule` SQLAlchemy 모델을 정의함. (id, name, description, entity_type, is_active)

2.  **API 스키마 추가**:
    *   `app/schemas/detection_rule.py` 파일을 생성하고, API 통신에 사용될 `DetectionRuleRead`, `DetectionRuleUpdate` Pydantic 스키마를 정의함.

3.  **클린 아키텍처 계층 구현**:
    *   **Repository**: `app/repositories/detection_rule_repository.py`를 생성하여 DB CRUD 로직을 구현함. (`get_all_rules`, `update_rule`)
    *   **Service**: `app/services/detection_rule_service.py`를 생성하여 비즈니스 로직(상태 변경)을 구현함.
    *   **UseCase**: `app/usecases/detection_rule_usecases.py`를 생성하여 서비스 로직을 조율하고 의존성 주입을 적용함.

4.  **API 라우터 구현**:
    *   `app/api/routers/detection_rules.py` 파일을 생성함.
    *   `GET /`: 모든 탐지 규칙 목록을 조회하는 API 엔드포인트를 구현함.
    *   `PATCH /{rule_id}`: 특정 규칙의 활성화 상태(`is_active`)를 수정하는 API 엔드포인트를 구현함.

5.  **애플리케이션 통합**:
    *   `app/main.py`에 신규 생성한 `detection_rules_router`를 `/api/v1/detection-rules` 경로로 등록하여 API를 활성화함.

### 후속 조치 (사용자)
*   `alembic revision --autogenerate -m "Create detection_rules table"` 명령어로 DB 마이그레이션 스크립트 생성 필요.
*   `alembic upgrade head` 명령어로 실제 DB에 `detection_rules` 테이블 생성 필요.

---

## 2025-10-16: 백엔드 API 문서 UI 수정

### 요약

백엔드 API 자동 문서(Swagger UI)에서 "Logs" 태그가 중복으로 표시되는 문제를 해결함. 이전의 프론트엔드 UI 수정은 착오였으므로 원상 복구함.

### 변경 사항

1.  **프론트엔드 코드 원상 복구**
    *   **파일**: `Admin-FE/frontend/app/dashboard/page.jsx`
    *   **내용**: 이전에 API 문서 문제를 프론트엔드 문제로 오인하여 수정했던 사이드바 메뉴의 `label`을 "전체 로그"에서 원래 값인 "전체 로그 페이지"로 되돌림.

2.  **백엔드 태그 중복 문제 해결**
    *   **파일**: `app/api/routers/logs.py`
    *   **내용**: `main.py`에서 라우터를 포함할 때 `tags=["Logs"]`를 설정하고, `logs.py`의 `APIRouter` 생성자에도 `tags=["logs"]`를 설정하여 태그가 중복으로 적용되는 것을 확인.
    *   **조치**: `logs.py`의 `APIRouter`에서 `tags` 인자를 제거하여, 태그 설정을 `main.py`로 일원화함.

---

## 2025-10-16: 런타임 에러 수정 (3)

### 요약

`uvicorn`으로 애플리케이션 실행 시 발생하는 `NameError`를 추가로 해결함.

### 변경 사항

*   **파일**: `app/api/routers/logs.py`
*   **내용**: `get_log_by_id` 및 다른 API 엔드포인트에서 `response_model`로 사용하는 `PIIDetectionLog` 등의 스키마 클래스에 대한 `import` 구문이 누락되어 `NameError`가 발생하는 것을 확인.
*   **조치**: 파일 상단에 `app.schemas.log`로부터 필요한 모든 스키마(`PIIDetectionLog`, `LogSearchResponse` 등)를 import하는 코드를 추가하여 문제를 해결함.

---

## 2025-10-16: 런타임 에러 수정 (2)

### 요약

`uvicorn`으로 애플리케이션 실행 시 발생하는 `NameError`를 추가로 해결함.

### 변경 사항

*   **파일**: `app/api/routers/logs.py`
*   **내용**: `logging` 모듈을 사용하기 전에 `import logging` 구문이 누락되어 `NameError`가 발생하는 것을 확인.
*   **조치**: 파일 상단에 `import logging`을 추가하여 문제를 해결함. 리팩토링 과정에서 발생한 실수로 추정됨.

---

## 2025-10-16: 런타임 에러 수정

### 요약

`uvicorn`으로 애플리케이션 실행 시 발생하는 `NameError`를 해결함.

### 변경 사항

*   **파일**: `app/services/log_service.py`
*   **내용**: `get_log_by_id` 메서드에서 사용하는 `PIIDetectionLog` 타입에 대한 `import` 구문이 누락되어 `NameError`가 발생하는 것을 확인.
*   **조치**: `app.schemas.log`로부터 `PIIDetectionLog`를 import하는 코드를 추가하여 문제를 해결함.

---

## 2025-10-16: 로그 서비스 고도화 및 API 개선

### 요약

프론트엔드(`Admin-FE`)와의 원활한 연동을 위해 백엔드 로그 서비스를 대대적으로 개선하고 클린 아키텍처 원칙에 따라 리팩토링을 진행함.

### 주요 변경 사항

1.  **클린 아키텍처 강화**
    *   **`usecases` 계층 추가**: `app/usecases/log_usecases.py`를 신규 생성하여 `Router`와 `Service` 사이의 비즈니스 흐름을 담당하는 유스케이스 계층을 명확히 함.
    *   **의존성 주입(DI) 적용**: FastAPI의 `Depends`를 사용하도록 `Router`, `UseCase`, `Service`를 전면 리팩토링하여 계층 간 결합도를 낮추고 테스트 용이성을 확보함.

2.  **API 기능 확장 및 개선**
    *   **단일 로그 조회 API 추가 (`GET /api/v1/logs/{log_id}`)**:
        *   프론트엔드에서 특정 로그의 상세 정보를 볼 수 있도록 ID 기반 조회 기능을 추가함.
        *   관련 `Repository`, `Service`, `UseCase`, `Router` 계층에 `get_log_by_id` 메서드 및 엔드포인트를 구현함.
    *   **로그 검색 API 개선 (`GET /api/v1/logs/search`)**:
        *   **동적 정렬 기능 추가**: `sort_by`, `sort_order` 쿼리 파라미터를 통해 사용자가 원하는 기준으로 로그를 정렬할 수 있게 함.
        *   **필터링 방식 개선**: `entity_types` 파라미터를 표준적인 다중 값 방식으로 처리하도록 수정함.
    *   **스키마 업데이트**: `app/schemas/log.py`의 `LogSearchRequest`에 정렬 관련 필드를 추가하여 API 명세를 명확히 함.

3.  **라우터 경로 수정**
    *   `main.py`와 `api/routers/logs.py`에 중복으로 선언되었던 URL 접두사(`prefix`)를 `main.py`에서만 관리하도록 수정하여 `/api/v1/logs/logs/*` 와 같은 비정상적인 경로가 생성되는 문제를 해결함.

### 기대 효과

*   프론트엔드에서 필요한 모든 로그 관련 기능(목록, 상세, 검색, 정렬)을 완벽하게 지원.
*   향후 유지보수 및 기능 확장이 용이한 견고한 아키텍처 확보.
