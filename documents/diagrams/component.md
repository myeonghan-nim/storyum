# 스토리움(Storyum) 컴포넌트 다이어그램

## 1. 문서 개요

**작성일**: 2025‑04‑24<br/>
**작성자**: hannim<br/>
**목적**: 스토리움(Storyum) 프로젝트의 컴포넌트 다이어그램을 작성하여 시스템 아키텍처를 시각적으로 표현<br/>
**범위**: 사용자 관리, 포스팅·알림 기능 및 이를 뒷받침할 인프라·성능·보안·운영·확장·통합 요구사항<br/>
**참고**: [Mermaid](https://mermaid-js.github.io/mermaid/#/) 문법을 사용하여 다이어그램을 작성<br/>

## 2. 컴포넌트 다이어그램

> 스토리움 SNS 서비스의 컴포넌트 다이어그램은 시스템의 주요 구성 요소와 그들 간의 관계를 나타냅니다.<br/>
> 이 다이어그램은 시스템 아키텍처를 이해하는 데 도움을 주며 각 컴포넌트의 역할과 상호작용을 명확히 합니다.<br/>
> 단, 이 다이어그램은 실제 구현과 다를 수 있으며 시스템의 복잡성에 따라 추가적인 세부 사항이 필요할 수 있습니다.<br/>

```mermaid
%% Storyum 컴포넌트 다이어그램
graph LR
  %% 1. Edge Layer
  subgraph Edge
    FE[Web Frontend]
    GW["API Gateway<br/>(Ingress / Nginx)"]
  end

  FE -- REST API / WebSocket --> GW

  subgraph Backend Core
    API["API Server<br/>(Django + DRF)"]
    Auth["Auth Module<br/>(JWT)"]
    User[User Service]
    Feed[Feed Service]
    Post["SNS Posting Service<br/>(Text / Poll / Media)"]
    Poll[Poll/Survey Service]
    Notify[Notification Service]
  end

  GW -- 요청 포워딩 --> API

  %% 인증/사용자
  API -- 토큰 발급/검증 --> Auth
  API -- 회원가입/팔로우·언팔로우/프로필 --> User
  User -- 사용자 데이터 CRUD --> DB

  %% 포스트/피드
  API -- 포스트 생성/조회 --> Post
  API -- 타임라인 피드 조회 --> Feed

  %% 3. Workers (Celery)
  subgraph Workers
    FeedWorker[Feed Worker]
    NotifyWorker[Notification Worker]
    MediaWorker[Media Worker]
  end

  %% 피드
  Post -- 포스트 CRUD --> DB
  Post -- Fan-out 요청 --> FeedWorker
  FeedWorker -- 팔로워별 캐시 생성 --> Cache

  Feed -- 캐시 조회 --> Cache
  Feed -- 캐시 미스 시 조회 --> DB
  Cache -- 피드 반환 --> Feed

  %% 알림
  Post -- 알림 이벤트 발행 --> Notify
  Notify -- MQ 발행 --> MQ
  MQ -- 이벤트 팬아웃 --> NotifyWorker
  NotifyWorker -- 푸시 --> External

  %% 미디어
  Post -- 미디어 업로드 --> Storage
  Post -- 미디어 이벤트 발행 --> MediaWorker
  MediaWorker -- 이미지 리사이징/비디오 트랜스코딩 --> Storage

  %% 4. Infra
  subgraph Infra
    DB[PostgreSQL]
    Cache["Redis<br/>(Caching + Pub/Sub)"]
    MQ[RabbitMQ]
    Storage[File Storage]
    Monitor[Prometheus + Grafana]
    Log[ELK Stack]
    Trace[OpenTelemetry Collector]
  end

  %% 모니터링/로깅
  API & Infra & Workers -- 데이터 전달 --> Trace
  Trace -- 메트릭 수집 --> Monitor
  Trace -- 로그 수집 --> Log
```
