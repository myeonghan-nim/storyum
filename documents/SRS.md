# 스토리움(Storyum) 요구사항 명세서 v1.0

## 1. 문서 개요

**작성일**: 2025‑04‑22<br/>
**작성자**: hannim<br/>
**목적**: 백엔드 개발 역량 강화를 위해 **스토리움** 프로젝트의 기능 및 비기능 요구사항을 구체적으로 정리<br/>
**범위**: 사용자 관리, 포스팅·알림 기능 및 이를 뒷받침할 인프라/성능/보안/운영/확장/통합 요구사항<br/>

## 2. 기능 요구사항

| ID | 기능 영역 | 기능 | 설명 | 입력 | 출력 | 우선순위 | 수용 기준 |
|:---:|:---:|:-----|:-----|:-----|:-----|:---:|:-----|
| FR-1 | 사용자 관리 | 회원가입 | 이메일/비밀번호/사용자 이름으로 신규 계정 생성 | email, password, confirm_password, username | 201 Created | 높음 | 정상 입력 → 201<br/>중복/불일치 입력 → 400 |
| FR-2 | 사용자 관리 | 로그인 | JWT 기반 인증 토큰 발급 | email, password | access_token, refresh_token | 높음 | 유효한 증명 → 200 + 토큰<br/>잘못된 증명 → 401 |
| FR-3 | 사용자 관리 | 로그아웃 | JWT 토큰을 받아 invalid 처리 | refresh_token | 204 No Content | 중 | 유효한 토큰 → 204<br/>잘못/만료된 토큰 → 401 |
| FR-4 | 사용자 관리 | 회원탈퇴 | 요청 시 계정 삭제, 탈퇴 시 OTP 확인 | access_token, TOTP code | 204 No Content | 중 | 인증 성공 → 204<br/>인증 실패 → 401 |
| FR-5 | 사용자 관리 | 프로필 조회/편집 | 사용자 이름, 프로필 이미지, 소개글 관리 | access_token, 수정 데이터 | 사용자 프로필 JSON | 중 | 권한 체크<br/>필수 필드 검증 |
| FR-6 | 사용자 관리 | 개인정보 수정 | 이메일, 비밀번호 변경 | access_token, 수정 데이터 | 사용자 개인정보 JSON | 중 | 권한 체크<br/>비밀번호 변경 시 기존 비밀번호 확인<br/>이메일 형식 검증 |
| FR-7 | 사용자 관리 | 팔로우/언팔로우 | 사용자 간 팔로우 관계 생성/삭제 | follower_id, followee_id | 200 OK | 중 | self-follow 금지<br/>이미 관계 존재 시 idempotent 처리 |
| FR-8 | 사용자 관리 | OTP 2차 인증 | TOTP(Google Authenticator) 기반 6자리 코드 검증 | access_token, TOTP code | 200 OK / 401 Unauthorized | 높음 | 30초 유효<br/>실패 5회 제한 후 잠금 |
| FR-9 | 포스팅(SNS) | 포스트/댓글 작성 및 인용 | 텍스트(최대 640자) 기반, 이미지/동영상(최대 10MB) 및 투표/설문(질문 + 최대5개 선택지, 단일/복수) 동시 포함 가능<br/>기존 포스트 댓글 가능(parent_post_id)<br/>기존 포스트 인용 가능(related_post_id) | access_token, parent_post_id?, related_post_id?, content, media_files[]?, question?, options[]?, multi_flag? | post_id, timestamp, parent_post_id?, related_post_id?, content, media_files[]?, question?, options[]?, multi_flag? | 높음 | 사용자 검증<br/>텍스트 필수<br/>미디어/설문 옵션<br/>파일/설문 검증 |
| FR-10 | 포스팅(SNS) | 좋아요 | 좋아요 토글 | access_token, post_id | post_id, like_count | 높음 | 좋아요 이중 클릭 방지 |
| FR-11 | 포스팅(SNS) | 해시태그/멘션 | `#tag`, `@username` 파싱 및 링크 처리 | access_token, post content | parsed content | 중 | 멘션 시 사용자 존재 검증 |
| FR-12 | 포스팅(SNS) | 피드 필터링 | 팔로우 대상, 인기 순, 키워드 알림 기반 필터링 | access_token, filter_type, keyword? | list of posts | 높음 | N+1 방지 인덱스, 페이지네이션 |
| FR-13 | 포스팅(SNS) | 검색 | 키워드/해시태그 검색 | q (string) | list of matched posts | 중 | 1단계: PostgreSQL FTS<br/>2단계: Elasticsearch (옵션) |
| FR-14 | 알림 | 팔로우 새 포스트 실시간 알림 | WebSocket/Redis Pub/Sub로 팔로워에게 실시간 푸시 | post_event | push to WS channel | 높음 | 연결 끊김 시 재연결 전략 |
| FR-15 | 알림 | 키워드/해시태그 알림 구독 | Celery + RabbitMQ 팬아웃, 백그라운드 매칭으로 알림 | access_token, keywords[] | notification records | 중 | 매칭 로직 정확성, 5분 지연 허용 |
| FR-16 | 알림 | 읽음/안읽음 처리 및 설정 | 사용자별 읽음 상태, 알림 유형별 On/Off | access_token, notification_id, action | 200 OK | 중 | 권한 검증 |

## 3. 비기능 요구사항

아래 항목을 간략히 포함하며 개발 단계에서 필요에 따라 세부 설정을 추가로 확장할 수 있도록 합니다.

### 3.1 API & 아키텍처

- RESTful 설계 및 버전 관리 (/api/v1)
- Swagger/OpenAPI 자동 문서화
- Mermaid Component/Sequence/ERD 다이어그램

### 3.2 인프라 구성

- Terraform (`terraform.tfstate` backend)으로 Docker Network/Volume Provisioning
- Docker Compose로 Django, PostgreSQL, Redis, RabbitMQ, ELK 스택, Prometheus + Grafana 서비스 구성
- Kubernetes (kind/minikube)로 배포 구성

### 3.3 성능 & 확장성

- Redis 캐싱 및 Django ORM 최적화
- 데이터베이스 파티셔닝 및 복합 인덱스 설계
- Kubernetes를 활용한 로드밸런싱 및 오토스케일링

### 3.4 가용성 & 신뢰성

- Rolling/Canary를 사용한 무중단 배포 (with PodDisruptionBudget)
- Liveness/Readiness Probe와 장애 재시도 로직 및 서킷 브레이커 패턴
- 데이터 백업 및 복구

### 3.5 보안

- SSL/TLS 전역 적용 및 JWT에서 인증/인가 강화
- 데이터 암호화 (at-rest, in-transit)
- Bandit 취약점 스캔

### 3.6 관측성 & 운영

- 로깅 및 모니터링/트레이싱 구성
- CI/CD 파이프라인 및 테스트

### 3.7 확장 & 통합

- Rate Limiting 및 메시징 (RabbitMQ/Kafka)
