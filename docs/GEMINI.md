# Gemini 개발 가이드: 클린 아키텍처

이 문서는 프로젝트의 일관성 있는 아키텍처를 유지하기 위한 개발 가이드입니다. 모든 기능 개발 및 수정 작업 시 아래의 아키텍처 원칙을 반드시 준수합니다.

---

## 0. 프로젝트 현황 분석 (2025-10-20)

### 1. 총평

- **목표:** 기능 명세서에 따라 프론트엔드 UI와 백엔드 API를 연결하여 완전한 기능을 구현하는 것.
- **아키텍처:** 백엔드와 프론트엔드 모두 `GEMINI.md`와 `ARCHITECTURE.md`에 정의된 클린 아키텍처를 잘 따르고 있어, 구조적으로 매우 견고함.
- **현황:** 백엔드는 주요 기능(인증, 로그, 규칙)의 API가 대부분 구현되어 있으나, 프론트엔드는 UI 뼈대만 있고 대부분의 데이터가 하드코딩된 목업 상태. **가장 시급한 문제는 프론트엔드 개발 환경의 불안정성.**

### 2. 백엔드 (`BE-main`)

- **기술 스택:**
    - **언어/프레임워크:** Python 3.13+, FastAPI
    - **데이터베이스:** PostgreSQL (SQLAlchemy, Alembic으로 관리), **Elasticsearch (로그 데이터용)**
    - **인증:** JWT (python-jose, passlib)
    - **AI:** PyTorch, Transformers (BERT 기반 NER 모델)
- **구현된 주요 기능:**
    - **인증:** 회원가입, 로그인 (`/api/v1/auth`)
    - **로그:** Elasticsearch를 사용한 로그 검색, 통계 (`/api/v1/logs`)
    - **탐지 규칙:** 규칙 조회 및 수정 (`/api/v1/detection-rules`)
    - **PII 탐지:** 핵심 PII 탐지 로직 (`/api/v1/pii`)
    - **통계 (신규):** '오늘 차단 횟수' 조회 (`/api/v1/metrics/blocks/today`)
- **상태:** 안정적. 클린 아키텍처 원칙에 따라 계층(Router-Usecase-Service-Repository)이 잘 분리되어 있어 기능 확장이 용이함.

### 3. 프론트엔드 (`Admin-FE`)

- **기술 스택:**
    - **프레임워크:** Next.js 15.2.4, React 19
    - **스타일링:** Tailwind CSS, shadcn/ui 컴포넌트
    - **상태 관리:** React Context API (`AuthContext`)
- **구현된 주요 기능:**
    - **페이지 구조:** 기능 명세에 맞는 대부분의 페이지(`dashboard`, `login`, `logs` 등)와 사이드바 메뉴가 UI 상으로 구현되어 있음.
    - **컴포넌트:** 로그인 폼, 대시보드의 각종 통계 카드 등 UI 컴포넌트들이 구현되어 있음.
    - **API 연동 상태:**
        - **'오늘 차단횟수' 위젯만** 백엔드 API와 연결됨.
        - 로그인, 회원가입을 포함한 **나머지 모든 기능은 하드코딩된 목업 데이터**를 사용 중.
- **상태 및 문제점:**
    - **치명적 문제:** `npm install` 시 **React 19 버전과 하위 의존성 간의 충돌**이 발생하여 개발 환경 구성이 불안정함. (`--legacy-peer-deps` 옵션으로 우회하고 있으나, 잠재적 런타임 오류의 원인이 됨)
    - 서버가 정상적으로 실행되지 않는 문제가 발생하여, 기능 확인이 어려운 상태.

### 4. 다음 단계 제안

1.  **[최우선] 프론트엔드 개발 환경 안정화:**
    - `node_modules`와 `package-lock.json`을 삭제하고 의존성을 재설치하여 깨끗한 환경에서 시작.
    - `npm run dev`를 포그라운드로 실행하여 에러 로그를 명확히 확인하고, 서버 실행 문제를 반드시 해결.
2.  **기능 구현 재개:**
    - 환경 안정화 후, '오늘 차단횟수' 기능이 정상 동작하는지 브라우저에서 확인.
    - 확인 완료 시, 계획했던 대로 '총 차단횟수' 위젯의 API 연동 작업을 이어서 진행.

---

## 1. 백엔드 아키텍처 (BE-main)

### 요청 처리 및 데이터 흐름

모든 요청은 다음의 계층형 아키텍처를 따라 처리됩니다.

**`Router → Usecases → Service → Repository → Model`**

### 각 계층의 역할과 책임 (SoC: Separation of Concerns)

1.  **`Router` (API 계층 - `app/api/routers/`)**: HTTP 요청 수신 및 응답 반환 (통신 담당)
2.  **`Usecases` (유스케이스 계층 - `app/usecases/`)**: 특정 기능 시나리오의 흐름 조율 (Orchestration)
3.  **`Service` (서비스 계층 - `app/services/`)**: 핵심 비즈니스 로직 수행
4.  **`Repository` (리포지토리 계층 - `app/repositories/`)**: 데이터 영속성(Persistence) 관리 (DB 통신 전담)
5.  **`Model` (모델 계층 - `app/models/`)**: 데이터 구조 정의

---

## 2. 프론트엔드 아키텍처 (Admin-FE)

### 기술 스택
- **프레임워크**: Next.js (React)
- **언어**: JavaScript (JSX)
- **스타일링**: Tailwind CSS
- **UI 컴포넌트**: Radix UI (headless), 직접 구현

### 계층 구조 및 역할

프론트엔드는 다음과 같은 관심사 분리 원칙을 따릅니다.

**`Page/Layout → Hook → Service → (API)`**

1.  **`app/` (라우팅 및 페이지 계층)**
    *   **책임**: 애플리케이션의 라우팅을 정의하고, 각 페이지의 전체적인 레이아웃을 구성합니다.
    *   **규칙**:
        *   `layout.jsx`: 여러 페이지에 걸쳐 공통적으로 사용되는 UI 셸(Shell)을 정의합니다. (예: 사이드바, 헤더)
        *   `page.jsx`: 특정 경로의 진입점(Entry Point)입니다. 데이터를 불러오고, 상태를 관리하며, 하위 컴포넌트들을 조합하여 하나의 완전한 페이지를 구성합니다.
        *   직접적인 UI 스타일링이나 복잡한 상태 로직은 포함하지 않고, 주로 데이터 흐름과 상태 관리를 담당합니다.

2.  **`components/` (UI 컴포넌트 계층)**
    *   **책임**: 재사용 가능한 UI 조각들을 정의합니다. (예: `Button`, `Card`, `Input`)
    *   **규칙**:
        *   이 컴포넌트들은 "Dumb Component"여야 합니다. 즉, 자체적으로 상태를 가지거나 API를 호출하지 않고, `props`로 받은 데이터와 콜백 함수에 따라서만 동작해야 합니다.
        *   애플리케이션의 특정 비즈니스 로직에 종속되지 않아야 합니다.

3.  **`hooks/` (로직 및 상태 관리 계층)**
    *   **책임**: 여러 컴포넌트에 걸쳐 재사용될 수 있는 상태 관련 로직(Stateful Logic)을 캡슐화합니다.
    *   **규칙**:
        *   React의 기본 Hook(`useState`, `useEffect` 등)을 조합하여 커스텀 Hook을 만듭니다. (예: `useApi`, `useForm`)
        *   API 호출, 폼 상태 관리, 이벤트 리스너 등 UI와 분리할 수 있는 로직을 이곳에 위치시킵니다.

4.  **`contexts/` (전역 상태 관리 계층)**
    *   **책임**: 애플리케이션 전반에서 공유되어야 하는 상태(예: 사용자 인증 정보, 테마)를 관리합니다.
    *   **규칙**:
        *   React Context API를 사용하여 Provider를 생성하고, 관련된 상태와 함수들을 함께 제공합니다.
        *   꼭 필요한 경우가 아니면, 페이지나 컴포넌트 레벨의 지역 상태(Local State)를 우선적으로 사용합니다.

5.  **`lib/` 또는 `services/` (외부 통신 및 유틸리티 계층)**
    *   **책임**: 백엔드 API 통신, 날짜 포맷팅 등 순수 유틸리티 함수들을 관리합니다.
    *   **규칙**:
        *   API 통신 함수들은 이곳에 모듈화하여 관리합니다. (예: `lib/api/logs.js`)
        *   API endpoint URL, 요청/응답 데이터 변환 등의 로직을 중앙에서 관리하여 일관성을 유지합니다.

---

## 3. API 명세 (API Specification) 가이드

### 정의
API 명세는 프론트엔드와 백엔드 간의 통신 규칙을 정의한 **공식 계약서** 또는 **상세 설명서**입니다. 개발의 효율성을 높이고 오류를 줄이기 위한 필수적인 문서입니다.

### 필수 포함 요소
- **엔드포인트 (Endpoint)**: API 주소 (e.g., `/api/v1/logs`)
- **HTTP 메서드 (Method)**: 작업 종류 (`GET`, `POST`, `PUT`, `DELETE`)
- **요청 (Request)**: 전송할 데이터의 JSON 구조 (백엔드의 `schemas`와 일치)
- **응답 (Response)**: 반환될 데이터의 JSON 구조

---

## 4. 주요 개발 목표 (Primary Development Goal)

### 핵심 목표
- **기능 명세 기반의 프론트엔드-백엔드 연동**: 사용자가 제공한 기능 명세서(https://docs.google.com/spreadsheets/d/1VHTV9fGUd5_R8xsS8JxkKuPBJm8w_BQ6WaoksF-KGYs/preview)를 기준으로, 현재 구현된 프론트엔드 UI와 백엔드 API를 연결하고 완전한 기능을 구현하는 것을 최우선 목표로 설정합니다.

### 기능 명세 상세
<details>
<summary>전체 기능 명세 보기</summary>

ID|기능 분류|기능 이름 (Feature)|화면 ID|우선순위|일정|상태|담당자|기능 설명 (Description)|사용자 스토리 (User Story)|수용 조건 (Acceptance Criteria)|종속성 (Dependencies)|비고 (Notes)|백엔드, 프론트엔드 공유 변수 명
---|---|---|---|---|---|---|---|---|---|---|---|---|---
FE-001|회원|로그인|L-01|최상|10/9|진행중|나재학|이메일과 비밀번호를 사용하여 서비스에 로그인하는 기능|사용자는 등록된 계정으로 로그인하여 개인화된 서비스를 이용할 수 있다.|1. 등록된 이메일과 비밀번호 일치 시 로그인 성공<br>2. 로그인 성공 시 메인 페이지로 이동<br>3. 이메일 또는 비밀번호 불일치 시 "계정 정보가 올바르지 않습니다." 오류 메시지 표시<br>4. 5회 연속 로그인 실패 시 계정 임시 잠금||소셜 로그인 기능은 별도 ID로 관리|
FE-002|회원|회원가입|R-01|최상|10/9|대기||신규 사용자가 서비스에 가입하는 기능|방문자는 개인 정보를 입력하여 새 계정을 생성하고 서비스를 이용하고 싶다.|1. 모든 필수 입력값(이름, 이메일, 비밀번호)이 유효해야 가입 버튼 활성화<br>2. 이메일 형식 유효성 검사<br>3. 비밀번호는 영문, 숫자, 특수문자 포함 8자 이상<br>4. 가입 완료 후 환영 이메일 발송|이메일 발송 서버||
|대시보드|분기별 유출 횟수|||10/10|||||||||
FE-003||총 차단회수||최상|10/10|대기|박성호<br><br>이선욱|감지했던 전체 차단횟수를 카운트하여, 대시보드에 표현하는것 ( 단위는 월별, 주별, 일별 구상중 )|관리자는 대시보드를 통해 관리하는 대상 및 단체의 전체 탐지 횟수를 한눈에서 편하게 확인 할 수 있다.|1. [Given] 기간 필터(일/주/월)가 선택됨 [When] 조회 버튼 클릭 [Then] 해당 기간의 총 차단 횟수 합계를 표시한다<br>2. [Given] 실시간 스트림 수신 [When] 신규 차단 이벤트 발생 [Then] 위젯 수치를 +1 증가시키고 1초 내 재렌더링한다<br>3. [Given] 데이터 과거 1년 존재 [When] 라인차트 탭 선택 [Then] 월별 추세 그래프를 표시한다(빈월=0 처리)<br>4. [Given] 권한=관리자 [When] CSV 다운로드 클릭 [Then] 기간/합계 컬럼으로 내보낸다<br>5. 백엔드 응답 실패 시 '데이터 없음' 상태와 재시도 버튼을 표시한다|- API: GET /api/metrics/blocks?from&to&interval=day|week|month<br>- DB: block_events(partitioned by day), materialized_view: mv_block_counts<br>- Cache: Redis key=metrics:blocks:<range> (TTL 60s)<br>- AuthZ: role=admin|viewer (다운로드는 admin만)|공유 변수명<br><br>total_block_count: number → 대시보드에 표시되는 총 차단 횟수 값<br>block_counts_timeseries : Array<{ts: string, count: number}> → 기간별(일/주/월) 차단 횟수를 시계열 데이터로 저장하는 배열<br>range_from : string(ISO8601) / range_to: string(ISO8601) → 조회 구간의 시작일자와 종료일자 (ISO 형식)<br>interval : 'day'|'week'|'month' → 집계 단위(일/주/월)
FE-004||IP 별 통계||최상||대기||IP 주소별 탐지 및 차단 기록을 집계하여 이상 트래픽을 모니터링하는 기능|관리자는 특정 IP에서 반복적인 공격 시도를 확인하고 보안 정책을 강화할 수 있다.|1. [Given] 기간 및 상위 N(기본 10) 선택 [When] 조회 [Then] 탐지/차단 횟수 상위 N IP를 표/바차트로 표시한다<br>2. [Given] 특정 IP 클릭 [When] 상세 보기 [Then] 해당 IP의 최근 이벤트 50건을 모달로 노출한다<br>3. 표 컬럼은 IP, 탐지횟수, 차단횟수, 마지막 탐지시각, 위험도 등급을 포함한다<br>4. CSV/XLSX 내보내기 시 현재 필터가 그대로 반영되어야 한다|- API: GET /api/metrics/ip-top?from&to&limit<br>- DB: block_events(ip), detection_events(ip)<br>- GeoIP(optional): 외부 Geo DB로 국가/도시 태깅<br>- Rate Limit: 상세 모달 조회 10req/min/IP|공유 변수명<br><br>ip_top_list: Array<{ip: string, detect_count: number, block_count: number, last_seen: string, risk: 'LOW'|'MID'|'HIGH'}> <br>→ 특정 기간 동안 탐지/차단 횟수가 가장 많은 IP 목록과 함께 탐지/차단 건수, 마지막 탐지 시각, 위험도 등급을 담은 리스트<br>selected_ip: string|null → 사용자가 상세 조회를 위해 선택한 특정 IP (없으면 null)<br>export_format: 'csv'|'xlsx' → 로그를 내보낼 때 선택한 파일 포맷
||오늘 차단횟수||최상||대기||금일 발생한 차단 건수를 실시간으로 표시하는 기능|관리자는 오늘의 보안 위협 수준을 빠르게 파악할 수 있다.|1. 서버 시간대(KST) 기준 00:00에 카운터가 0으로 초기화된다<br>2. 신규 차단 이벤트가 들어오면 1초 이내 UI가 증가치를 반영한다<br>3. API 실패 시 마지막 성공 값과 '오프라인' 배지를 함께 표시한다|- API: GET /api/metrics/blocks/today<br>- Stream: SSE/WebSocket topic=blocks.new<br>- Time: 서버/클라이언트 타임존 동기화(KST)|공유 변수명<br><br>today_block_count: number → 금일(서버 기준 00:00 이후) 집계된 차단 횟수<br>is_realtime_connected: boolean → 실시간 스트림(WebSocket/SSE) 연결 상태
||최근 알림( 위험 감지)||중||대기||가장 최근 발생한 탐지 이벤트를 알림 형식으로 제공|관리자는 즉시 최근 발생한 보안 위협을 파악하고 대응할 수 있다.|1. 최신 10건을 시간 내림차순으로 표시하며, 미확인 상태는 강조 스타일로 구분한다<br>2. 알림 클릭 시 상세 로그 페이지로 라우팅된다(쿼리스트링으로 이벤트 ID 전달)<br>3. 알림에는 이벤트시각, 소스(IP/사용자), 라벨, 위험도, 요약문이 포함된다<br>4. 실시간 스트림 수신 시 리스트 상단에 prepend하고 총 50건까지만 보관한다|- API: GET /api/alerts/recent?limit=10<br>- Stream: WebSocket topic=alerts.new<br>- DB: alerts, detections(join)|공유 변수명<br><br>recent_alerts: Array<{id: string, ts: string, source: string, label: string, severity: 'LOW'|'MID'|'HIGH', summary: string, read: boolean}> <br>→ 최근 탐지된 알림 내역(이벤트 ID, 발생 시각, 출처 IP/사용자, 탐지 라벨, 심각도, 요약, 읽음 여부)을 담은 배열
|대시보드_라벨 통계|전체 라벨 건수(무시 단순라벨)||최상||대기||탐지된 전체 라벨 건수를 집계하여 대시보드에 표시|관리자는 특정 기간 동안 전체 라벨 탐지 건수를 확인할 수 있다.|1. 기간 필터와 연동되며, 선택한 기간의 라벨 총합을 표시한다<br>2. 라벨 미존재 시 0으로 표시하고 안내 문구를 보여준다<br>3. 다운로드 시 label,total_count 컬럼 포함 CSV 제공|- API: GET /api/metrics/labels/total?from&to<br>- DB: detection_labels(label, created_at)|공유 변수명<br><br>total_label_count: number → 특정 기간 동안 탐지된 라벨의 총 개수
||가장 많이 탐지된라벨||최상||대기||탐지된 라벨 중 빈도가 가장 높은 항목을 표시|관리자는 어떤 유형의 탐지 이벤트가 가장 빈번히 발생하는지 파악할 수 있다.|1. Top N(기본 5) 라벨과 각 건수를 막대그래프로 표시한다<br>2. 라벨 툴팁에 예시 샘플 1건의 요약문을 노출한다<br>3. 특정 라벨 클릭 시 해당 라벨 필터가 적용된 로그 페이지로 이동한다|- API: GET /api/metrics/labels-top?from&to&limit<br>- DB: detection_labels(label) with index<br>- Search: Elastic/Opensearch (라벨별 샘플 조회)|공유 변수명<br><br>label_top_list: Array<{label: string, count: number, sample_event_id: string|null}> <br>→ 특정 기간 동안 가장 많이 탐지된 라벨과 탐지 건수, 샘플 이벤트 ID(없을 경우 null)를 담은 리스트<br>label_top_limit: number → 조회할 상위 라벨 개수 (예: 5, 10 등)
|전체 로그 페이지|로그 엑셀 표<br>[ IP , 탐지 시간, 전체 프롬프트,<br>탐지된 내용 , 판정( 정탐 오탐) ]||상|10/12|대기|박성호<br><br>나재학|||||||
||상단 필터링 검색 기능||상||대기||대시보드 상단에서 로그 데이터를 조건별로 검색할 수 있는 기능|관리자는 특정 기간, IP, 라벨 기준으로 로그를 신속히 검색할 수 있다.|1. 기간, IP, 라벨, 결정(ALLOW/BLOCK) 필터를 조합 적용할 수 있다<br>2. 필터 적용/초기화 시 URL 쿼리스트링이 동기화되어 공유가 가능하다<br>3. 유효하지 않은 입력(IP 포맷 등)은 즉시 검증하여 에러 메시지를 보여준다|- Client: URL query sync (router)<br>- Server: 모든 목록 API는 동일 필터 파라미터 스키마를 수용<br>- Validation: 공용 유효성 모듈(ipv4/ipv6, date-range)|공유 변수명<br><br>filter_from: string(ISO) / filter_to: string(ISO) → 검색 구간 시작/종료 시각<br>filter_ip: string|null → 특정 IP 기준 필터 값<br>filter_label: string|null → 특정 라벨 기준 필터 값<br>filter_decision: 'ALLOW'|'BLOCK'|null → 탐지 결과 기준 필터 값 (허용/차단/전체)
||정렬 기능||상||대기||로그 데이터를 원하는 기준(시간, IP, 라벨)으로 정렬할 수 있는 기능|관리자는 탐지 로그를 원하는 기준에 따라 정렬해 효율적으로 분석할 수 있다.|1. 각 컬럼 헤더 클릭 시 오름/내림차순 전환, 다중 정렬은 Shift+클릭으로 지정한다<br>2. 정렬 상태는 URL과 로컬 스토리지에 동기화되어 새로고침에도 유지된다<br>3. 서버 응답은 정렬 필드를 화이트리스트로 검증한다|- API: 목록 엔드포인트 정렬 파라미터 지원<br>- Client: 정렬 상태 저장 로직(localStorage)|공유 변수명<br><br>sort_fields: Array<{field: string, order: 'asc'|'desc'}> <br>→ 정렬에 사용되는 기준 필드와 정렬 순서(오름/내림차순)를 담은 배열
|탐지 기능 설정<br>[ NER ]|라벨별 차단 여부||최상||대기|박성호<br><br>이선욱|탐지된 각 라벨에 대해 차단 여부를 설정할 수 있는 기능|관리자는 특정 라벨 탐지 시 자동 차단 여부를 정책에 맞게 설정할 수 있다.|1. 라벨 행의 토글 스위치로 차단 ON/OFF 전환 시 300ms 내 UI에 반영한다<br>2. 저장 실패 시 롤백하고 에러 토스트를 표시한다<br>3. 정책 변경 이력은 사용자/시각/이전→변경값을 기록한다|- API: PATCH /api/policy/labels/{label} {block: boolean}<br>- DB: policy_label_rules(label, block) + audit_trail<br>- AuthZ: role=admin|공유 변수명<br><br>label_rules: Record<string, {block: boolean}> <br>→ 라벨별 차단 정책 상태를 담은 객체 (라벨명 → 차단 여부 true/false)
||로그 여부||최상||대기||탐지 이벤트를 로그에 저장할지 여부를 설정|관리자는 로그 저장을 통해 사후 분석이 필요한 경우 데이터를 남길 수 있다.|1. 글로벌 토글 ON일 때만 탐지 이벤트가 영구 저장된다<br>2. OFF 상태에서도 실시간 탐지/차단 동작에는 영향이 없어야 한다<br>3. 상태 변경은 감사 로그에 남긴다|- API: PATCH /api/policy/logging {enabled: boolean}<br>- DB: system_settings(logging_enabled), audit_trail|공유 변수명<br><br>logging_enabled: boolean → 로그 저장 기능 활성화 여부
||가명화 여부||하||대기||탐지된 데이터 중 민감 정보를 가명화하여 저장 여부를 설정|관리자는 개인정보 보호를 위해 탐지 로그의 일부 데이터를 가명화할 수 있다.|1. ON일 때 저장/조회 모두 마스킹이 적용된다(권한 예외: auditor)<br>2. 마스킹 규칙: 이름→이*민, 전화번호→010-****-1234 등 규칙 기반<br>3. 다운로드 시에도 동일 규칙 적용(예외 권한은 원문 다운로드 가능)|- API: PATCH /api/policy/pseudonymize {enabled: boolean}<br>- Masking: 규칙 엔진(정규식/NER)<br>- AuthZ: role=auditor 예외 처리|공유 변수명<br><br>pseudonymize_enabled: boolean → 가명화 기능 활성화 여부
|탐지 기능 설정<br>[ 맥락 ]|차단할 맥락 프롬프트 입력 및 수정||최상||대기||관리자가 직접 차단할 맥락 프롬프트를 등록 및 수정하는 기능|관리자는 특정 패턴의 프롬프트가 탐지되었을 때 자동 차단되도록 정책을 설정할 수 있다.|1. 신규 등록 시 중복/공백/금지어를 검증한다<br>2. 정규식/키워드/벡터(유사도) 3가지 타입을 지원한다<br>3. 삭제/수정 시 즉시 실시간 엔진에 반영된다(무중단)<br>4. 테스트 버튼을 눌러 샘플 프롬프트에 대한 매칭 결과를 즉시 확인할 수 있다|- API: POST/PUT/DELETE /api/policy/context-prompts<br>- Engine: 실시간 필터 리로딩 훅<br>- DB: context_prompt_rules(id, type, pattern, created_by, updated_at)|공유 변수명<br><br>context_rules: Array<{id: string, type: 'regex'|'keyword'|'vector', pattern: string, enabled: boolean}> <br>→ 차단 규칙 목록 (고유 ID, 규칙 유형[정규식/키워드/벡터], 패턴, 활성화 여부 포함)<br><br>test_prompt: string → 사용자가 입력한 테스트 프롬프트 (차단 규칙 적용 여부 확인용)
||차단할 정책 파일 업로드 및 삭제 수정||최상||대기|||||||
||자연어 맥락 처리||중||대기|||||||

</details>
