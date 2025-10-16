# 개발 로그 (Development Log)

이 문서는 프로젝트의 모든 개발 및 수정 이력을 기록합니다.

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
