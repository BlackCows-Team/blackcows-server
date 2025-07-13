# 🐄 BlackCows 젖소 관리 시스템 API

> **Flutter 앱과 연동되는 종합적인 젖소 관리 및 기록 시스템 REST API 서버**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.3.1-green.svg)](https://fastapi.tiangolo.com)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 프로젝트 개요

BlackCows는 낙농업 종합 관리 시스템으로, 젖소 정보 관리와 다양한 상세 기록 관리를 지원하는 RESTful API 서버입니다. Google, Kakao, Naver SNS 로그인을 지원하여 사용자 편의성을 극대화했습니다.

### 🎯 주요 기능

### 🛠️ 관리자/운영자용 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/admin/token-stats` | **토큰 통계 조회** | Bearer Token | 리프레시 토큰 통계 |
| `POST` | `/admin/cleanup-tokens` | **토큰 정리 실행** | Bearer Token | 정리 결과 |
| `DELETE` | `/admin/revoke-user-tokens/{user_id}` | **사용자 토큰 무효화** | `user_id` + Bearer Token | 무효화 결과 |
| `POST` | `/auth/admin/cleanup-temporary-passwords` | **임시 비밀번호 정리** | Bearer Token | 정리 결과 |

#### 관리자 기능 특징
- ✅ **토큰 관리**: 만료된/오래된 토큰 자동 정리
- ✅ **보안 관리**: 특정 사용자 토큰 무효화
- ✅ **시스템 정리**: 임시 비밀번호 등 정리
- ✅ **모니터링**: 토큰 사용 현황 통계

#### 📢 알림 시스템 (NEW!)
- ✅ **다중 채널 알림** - 앱 내, 이메일, 푸시 알림 지원
- ✅ **FCM 푸시 알림** - Firebase Cloud Messaging 기반 실시간 푸시
- ✅ **자동 알림** - 할일 마감, 지연, 일일/주간 요약 자동 발송
- ✅ **수동 알림** - 관리자가 직접 알림 생성 및 일괄 발송
- ✅ **알림 설정** - 사용자별 채널/유형/시간대 설정
- ✅ **통계 및 분석** - 알림 발송 현황 및 사용자 반응 분석
- ✅ **토픽 구독** - 특정 주제별 알림 구독/해제
- ✅ **스케줄러** - APScheduler 기반 자동 알림 발송

### 🛠️ 관리자/운영자용 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/admin/token-stats` | **토큰 통계 조회** | Bearer Token | 리프레시 토큰 통계 |
| `POST` | `/admin/cleanup-tokens` | **토큰 정리 실행** | Bearer Token | 정리 결과 |
| `DELETE` | `/admin/revoke-user-tokens/{user_id}` | **사용자 토큰 무효화** | `user_id` + Bearer Token | 무효화 결과 |
| `POST` | `/auth/admin/cleanup-temporary-passwords` | **임시 비밀번호 정리** | Bearer Token | 정리 결과 |

#### 관리자 기능 특징
- ✅ **토큰 관리**: 만료된/오래된 토큰 자동 정리
- ✅ **보안 관리**: 특정 사용자 토큰 무효화
- ✅ **시스템 정리**: 임시 비밀번호 등 정리
- ✅ **모니터링**: 토큰 사용 현황 통계

#### 📋 할일 관리 시스템 (NEW!)
- ✅ **할일 생성 및 관리** - 제목, 설명, 마감일, 우선순위 설정
- ✅ **할일 유형 분류** - 개인/젖소별/농장 전체 할일
- ✅ **젖소 연결** - 할일과 관련된 젖소 연결 기능
- ✅ **상태 관리** - 대기중, 진행중, 완료, 취소, 지연 등 상태 추적
- ✅ **우선순위 설정** - 낮음, 보통, 높음, 긴급 우선순위 지정
- ✅ **카테고리 분류** - 착유, 치료, 백신, 검진, 번식, 사료, 시설관리 등
- ✅ **반복 일정** - 매일/주/월/년 반복 할일 설정
- ✅ **마감일/시간** - 정확한 마감일시 설정 및 지연 자동 감지
- ✅ **통계 및 분석** - 완료율, 카테고리별 분포, 우선순위별 분석
- ✅ **캘린더 뷰** - 날짜별 할일 그룹화 및 시각화
- ✅ **자동 지연 감지** - 마감일 지난 할일 자동 상태 변경

#### 🐮 젖소 기본 관리
- ✅ **젖소 등록/수정/삭제** - 이표번호, 센서번호, 기본 정보 관리
- ✅ **축산물이력제 연동** - 이표번호로 축산물품질평가원 API 조회 및 자동 등록
- ✅ **3단계 젖소 등록 플로우** - 축산물이력제 우선, 수동 등록 대안
- ✅ **즐겨찾기 시스템** - 홈화면 노출용 젖소 선별
- ✅ **상세 정보 관리** - 체중, 산차, 성격, 위치 등 확장 정보
- ✅ **검색 및 통계** - 이표번호 검색, 농장별 통계 제공

#### 📊 상세 기록 관리 (10가지 유형)
- 🥛 **착유 기록** - 착유량, 유지방, 유단백, 체세포수 등 **[필수: 착유날짜, 착유량]**
- 💕 **발정 기록** - 발정 강도, 지속시간, 행동 징후 등
- 🎯 **인공수정 기록** - 종축 정보, 정액 품질, 성공 확률 등
- 🤱 **임신감정 기록** - 감정 방법, 결과, 분만예정일 등
- 👶 **분만 기록** - 분만 난이도, 송아지 정보, 합병증 등
- 🌾 **사료급여 기록** - 사료 종류, 급여량, 첨가제 등
- 🏥 **건강검진 기록** - 체온, 심박수, 체형점수 등
- 💉 **백신접종 기록** - 백신명, 접종량, 부작용 등
- ⚖️ **체중측정 기록** - 체중, 체척, 증체율 등
- 🩺 **치료 기록** - 진단명, 사용약물, 치료비용 등

#### 📝 기본 기록 관리 (4가지 유형)
- 🔄 **번식 기록** - 인공수정, 자연교배, 번식 결과 등
- 🏥 **질병 기록** - 질병명, 증상, 치료내용, 심각도 등
- 📊 **분류변경 기록** - 젖소 상태 변경 이력, 변경 사유 등
- 📋 **기타 기록** - 위 분류에 속하지 않는 특별한 기록

#### 🔗 축산물이력제 연동 기능
- ✅ **소 기본 개체정보** - 이표번호, 출생일, 품종, 성별, 개월령 자동계산
- ✅ **농장 등록 이력** - 여러 농장 이동 이력 추적
- ✅ **도축 및 포장 처리 정보** - 도축장, 등급, 근내지방도, 위생검사 결과
- ✅ **구제역 백신 접종 정보** - 최종접종일, 접종차수, 경과일
- ✅ **럼피스킨 백신 접종 정보** - 최종접종일 정보
- ✅ **브루셀라 검사 정보** - 검사일, 결과, 경과일 자동계산
- ✅ **결핵 검사 정보** - 검사일, 결과
- ✅ **질병 정보** - 질병유무 상태
- ✅ **수입축 정보** - 수입국가, 수입경과월

#### 🤖 AI 챗봇 기능 "소담이" (NEW!)
- ✅ **낙농업 전문 AI 어시스턴트** - OpenAI GPT-4o-mini 기반 지능형 대화
- ✅ **LangGraph 대화 플로우** - 고도화된 질문 분류 및 응답 시스템
- ✅ **4가지 질문 분류 시스템**:
  - **낙농 지식 (rag)**: 낙농업 관련 전문 정보 제공
  - **농장 데이터 (cow_info)**: 사용자 목장의 젖소 정보 및 기록 조회
  - **일반 대화 (general)**: 인사, 잡담, 챗봇 소개 등
  - **무관한 질문 (irrelevant)**: 낙농과 무관한 질문에 대한 안내
- ✅ **한국어 전용 지원** - 낙농업 전문용어에 특화된 한국어 대화
- ✅ **채팅방 관리** - 개별 대화방 생성, 이력 관리, 자동 정리
- ✅ **메모리 기반 연속 대화** - 대화 맥락을 유지하는 지능형 응답
- ✅ **농장 데이터 연동** - 사용자의 젖소 정보와 기록을 바탕으로 한 맞춤형 답변

#### 🔐 보안 및 인증
- ✅ **JWT 기반 사용자 인증** - Access/Refresh Token
- ✅ **SNS 로그인 지원** - Google, Kakao, Naver 3개 플랫폼 지원
- ✅ **Firebase Admin SDK 연동** - Google 토큰 자동 검증
- ✅ **농장별 데이터 격리** - 멀티테넌트 지원
- ✅ **Firebase 보안 규칙** - 데이터 접근 제어
- ✅ **비밀번호 재설정** - 이메일 기반 토큰 시스템
- ✅ **회원탈퇴** - 모든 관련 데이터 완전 삭제

## 📡 전체 API 엔드포인트

### 📋 할일 관리 API (`/api/todos`) - ⭐ NEW!

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/api/todos/test-auth` | **인증 테스트** | Bearer Token | 인증 상태 확인 |
| `POST` | `/api/todos/create` | **할일 생성** | `title`, `task_type`, `priority`, `category` + Bearer Token | 생성된 할일 정보 |
| `GET` | `/api/todos/` | **할일 목록 조회** | Bearer Token | 필터링된 할일 목록 |
| `GET` | `/api/todos/today` | **오늘 할일 조회** | Bearer Token | 오늘 마감인 할일 목록 |
| `GET` | `/api/todos/overdue` | **지연된 할일 조회** | Bearer Token | 마감일 지난 할일 목록 |
| `GET` | `/api/todos/statistics` | **할일 통계 조회** | Bearer Token | 통계 정보 (완료율, 분포 등) |
| `GET` | `/api/todos/calendar` | **캘린더 뷰 조회** | `start_date`, `end_date` + Bearer Token | 날짜별 할일 그룹 |
| `GET` | `/api/todos/{task_id}` | **할일 상세 조회** | `task_id` + Bearer Token | 특정 할일 상세 정보 |
| `PUT` | `/api/todos/{task_id}/update` | **할일 수정** | `task_id` + Bearer Token | 수정된 할일 정보 |
| `PATCH` | `/api/todos/{task_id}/complete` | **할일 완료 처리** | `task_id` + Bearer Token | 완료된 할일 정보 |
| `DELETE` | `/api/todos/{task_id}` | **할일 삭제** | `task_id` + Bearer Token | 삭제 확인 메시지 |

#### 할일 관리 특징
- ✅ **개인/젖소별/농장 전체 할일** - 할일 유형별 분류
- ✅ **우선순위 시스템** - 낮음/보통/높음/긴급
- ✅ **카테고리 분류** - 착유, 치료, 백신, 검진, 번식, 사료, 시설관리, 일반, 기타
- ✅ **반복 일정** - 매일/주/월/년 반복 설정
- ✅ **자동 지연 감지** - 마감일 지난 할일 자동 상태 변경
- ✅ **젖소 연결** - 특정 젖소와 연관된 할일 설정
- ✅ **통계 및 분석** - 완료율, 카테고리별 분포, 우선순위별 분석
- ✅ **캘린더 뷰** - 날짜별 할일 그룹화 및 시각화

#### 할일 생성 예시
```json
POST /api/todos/create
{
  "title": "103번 소 착유 체크",
  "description": "오전 6시 착유량 확인",
  "task_type": "cow_specific",
  "priority": "high",
  "due_date": "2024-01-20",
  "due_time": "06:00",
  "category": "milking",
  "related_cow_id": "cow-uuid-123",
  "recurrence": "daily",
  "notes": "매일 정기 착유 체크"
}
```

#### 할일 통계 응답 예시
```json
{
  "total_tasks": 25,
  "pending_tasks": 8,
  "completed_tasks": 15,
  "overdue_tasks": 2,
  "today_tasks": 3,
  "high_priority_tasks": 5,
  "completion_rate": 60.0,
  "by_category": {
    "milking": 10,
    "treatment": 5,
    "vaccination": 3,
    "general": 7
  },
  "by_priority": {
    "low": 5,
    "medium": 12,
    "high": 6,
    "urgent": 2
  }
}
```

### 🔐 인증 관리 API (`/auth`)

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/auth/register` | 회원가입 (목장별명 포함) | `username`, `user_id`, `email`, `password`, `password_confirm` | 사용자 정보 + 농장 정보 |
| `POST` | `/auth/login` | 로그인 (user_id 기반) | `user_id`, `password` | `access_token`, `refresh_token`, 사용자 정보 |
| `POST` | `/auth/refresh` | 토큰 갱신 | `refresh_token` | 새로운 `access_token` |
| `GET` | `/auth/me` | 현재 사용자 정보 조회 | Bearer Token | 현재 사용자 정보 |
| `POST` | `/auth/find-user-id` | 아이디 찾기 | `username`, `email` | 찾은 `user_id` |
| `POST` | `/auth/request-password-reset` | 비밀번호 재설정 요청 | `username`, `user_id`, `email` | 이메일 전송 결과 + 임시 토큰 |
| `POST` | `/auth/verify-reset-token` | 재설정 토큰 검증 | `token` | 토큰 유효성 결과 |
| `POST` | `/auth/reset-password` | 비밀번호 재설정 | `token`, `new_password`, `confirm_password` | 재설정 성공 메시지 |
| `POST` | `/auth/login-with-reset-token` | 임시 토큰 로그인 | `user_id`, `reset_token` | 임시 `access_token` (비밀번호 변경 권한) |
| `POST` | `/auth/change-password` | 비밀번호 변경 | `new_password`, `confirm_password` + Bearer Token | 변경 성공 메시지 |
| `PUT` | `/auth/update-farm-name` | 목장 이름 수정 | `farm_nickname` + Bearer Token | 수정된 사용자 정보 |
| `DELETE` | `/auth/delete-account` | 회원탈퇴 | `password`, `confirmation` + Bearer Token | 삭제 완료 메시지 |
| `POST` | `/auth/login-debug` | 로그인 디버깅 | 원시 요청 데이터 | 디버그 정보 |

#### 📧 임시비밀번호 및 이메일 시스템 (업데이트!)

**임시비밀번호 생성 플로우:**
1. **비밀번호 재설정 요청**: 사용자가 이름, 아이디, 이메일 입력
2. **사용자 검증**: 서버에서 3개 정보 모두 일치하는지 확인
3. **JWT 토큰 생성**: 1시간 유효한 재설정 토큰 생성
4. **이메일 발송**: AWS SES 또는 Gmail SMTP로 재설정 링크 발송
5. **토큰 검증**: 사용자가 링크 클릭 시 토큰 유효성 검증
6. **임시 로그인**: 재설정 토큰으로 제한된 권한 로그인
7. **비밀번호 변경**: 새 비밀번호로 변경 완료
8. **보안 강화**: 모든 기존 리프레시 토큰 무효화

**이메일 서비스 구성:**
- **AWS SES**: 프로덕션 환경 이메일 발송
- **Gmail SMTP**: 개발 환경 및 백업 서비스
- **템플릿 시스템**: HTML 이메일 템플릿 지원
- **발송 추적**: 이메일 발송 성공/실패 로그 관리

**비밀번호 재설정 요청 예시:**
```json
POST /auth/request-password-reset
{
  "username": "홍길동",
  "user_id": "admin123", 
  "email": "admin@farm.com"
}
```

**응답:**
```json
{
  "success": true,
  "message": "비밀번호 재설정 이메일이 발송되었습니다.",
  "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-07-12T15:30:00Z"
}
```

**임시 토큰 로그인 예시:**
```json
POST /auth/login-with-reset-token
{
  "user_id": "admin123",
  "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답:**
```json
{
  "access_token": "temporary_access_token_here",
  "token_type": "bearer",
  "expires_in": 1800,
  "scope": "password_change_only",
  "user": {
    "user_id": "admin123",
    "username": "홍길동",
    "email": "admin@farm.com"
  }
}
```

### 📱 SNS 로그인 API (`/sns`)

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/sns/google/login` | Google 소셜 로그인 | `access_token` | JWT Token + 사용자 정보 + 농장 정보 |
| `DELETE` | `/sns/delete-account` | SNS 계정 연동 해제 및 탈퇴 | `provider`, `access_token` | 삭제 완료 메시지 |

#### SNS 로그인 특징
- ✅ **자동 사용자 생성** - 첫 로그인 시 사용자 및 농장 정보 자동 생성
- ✅ **토큰 자동 검증** - 각 플랫폼 API를 통한 액세스 토큰 유효성 검증
- ✅ **JWT 토큰 발급** - Access Token + Refresh Token 자동 발급
- ✅ **프로필 정보 동기화** - SNS 프로필 정보를 사용자 정보에 자동 반영
- ✅ **농장 정보 자동 생성** - 첫 로그인 시 기본 농장 정보 자동 설정

**지원 플랫폼:**
- **Google**: Firebase Admin SDK를 통한 ID Token 검증


### 🐮 젖소 관리 API (`/cows`)

#### 축산물이력제 연동 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/cows/registration-status/{ear_tag_number}` | 젖소 등록 상태 확인 | `ear_tag_number` + Bearer Token | 등록 상태 (already_registered/livestock_trace_available/manual_registration_required) |
| `POST` | `/cows/register-from-livestock-trace` | 축산물이력제 정보 기반 젖소 등록 | `ear_tag_number`, `user_provided_name` + Bearer Token | 등록된 젖소 정보 + 축산물이력제 데이터 |

#### 기본 젖소 관리 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/cows/manual` | 젖소 수동 등록 | `ear_tag_number`, `name` | 등록된 젖소 정보 |
| `POST` | `/cows/` | 젖소 등록 (레거시) | `ear_tag_number`, `name` | 등록된 젖소 정보 |
| `GET` | `/cows/` | 젖소 목록 조회 | Bearer Token | 농장 내 모든 젖소 목록 |
| `GET` | `/cows/{cow_id}` | 젖소 상세 조회 | `cow_id` + Bearer Token | 특정 젖소 상세 정보 |
| `PUT` | `/cows/{cow_id}` | 젖소 정보 수정 | `cow_id` + Bearer Token | 수정된 젖소 정보 |
| `DELETE` | `/cows/{cow_id}` | 젖소 삭제 (소프트 삭제) | `cow_id` + Bearer Token | 삭제 확인 메시지 |
| `PATCH` | `/cows/{cow_id}/favorite` | 즐겨찾기 토글 | `cow_id` + Bearer Token | 즐겨찾기 상태 변경 결과 |
| `GET` | `/cows/favorites/list` | 즐겨찾기 젖소 목록 | Bearer Token | 즐겨찾기된 젖소들 |
| `GET` | `/cows/search/by-tag/{ear_tag_number}` | 이표번호로 젖소 검색 | `ear_tag_number` + Bearer Token | 검색된 젖소 정보 |
| `GET` | `/cows/statistics/summary` | 농장 통계 조회 | Bearer Token | 전체/건강상태별/번식상태별 통계 |

#### 젖소 상세정보 관리 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `PUT` | `/cows/{cow_id}/details` | 젖소 상세정보 업데이트 | `cow_id` + Bearer Token | 업데이트된 상세정보 |
| `GET` | `/cows/{cow_id}/details` | 젖소 상세정보 조회 | `cow_id` + Bearer Token | 전체 상세정보 포함 젖소 데이터 |
| `GET` | `/cows/{cow_id}/has-details` | 상세정보 보유 여부 확인 | `cow_id` + Bearer Token | `has_detailed_info` boolean |
| `GET` | `/cows/{cow_id}/livestock-trace-info` | 젖소의 축산물이력제 정보 조회 | `cow_id` + Bearer Token | 축산물이력제 연동 정보 |

### 📝 상세 기록 관리 API (`/records`)

#### 🥛 착유 기록 (핵심 기능)
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/milking` | 착유 기록 생성 | `cow_id`, `record_date`, `milk_yield` | 생성된 착유 기록 |
| `GET` | `/records/cow/{cow_id}/milking` | 젖소별 착유 기록 조회 | `cow_id` + Bearer Token | 특정 젖소의 착유 기록 목록 |
| `GET` | `/records/milking/recent` | 최근 착유 기록 조회 | Bearer Token | 농장 전체 최근 착유 기록 |

#### 💕 발정 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/estrus` | 발정 기록 생성 | `cow_id`, `record_date` | 생성된 발정 기록 |

#### 🎯 인공수정 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/insemination` | 인공수정 기록 생성 | `cow_id`, `record_date` | 생성된 인공수정 기록 |

#### 🤱 임신감정 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/pregnancy-check` | 임신감정 기록 생성 | `cow_id`, `record_date` | 생성된 임신감정 기록 |

#### 👶 분만 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/calving` | 분만 기록 생성 | `cow_id`, `record_date` | 생성된 분만 기록 |

#### 🌾 사료급여 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/feed` | 사료급여 기록 생성 | `cow_id`, `record_date` | 생성된 사료급여 기록 |

#### 🏥 건강검진 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/health-check` | 건강검진 기록 생성 | `cow_id`, `record_date` | 생성된 건강검진 기록 |

#### 💉 백신접종 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/vaccination` | 백신접종 기록 생성 | `cow_id`, `record_date` | 생성된 백신접종 기록 |

#### ⚖️ 체중측정 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/weight` | 체중측정 기록 생성 | `cow_id`, `record_date` | 생성된 체중측정 기록 |

#### 🩺 치료 기록
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/records/treatment` | 치료 기록 생성 | `cow_id`, `record_date` | 생성된 치료 기록 |

### 📋 기록 조회 및 관리 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/records/cow/{cow_id}` | 젖소별 전체 기록 조회 | `cow_id` + Bearer Token | 특정 젖소의 모든 기록 목록 |
| `GET` | `/records/{record_id}` | 기록 상세 조회 | `record_id` + Bearer Token | 특정 기록의 상세 정보 |
| `PUT` | `/records/{record_id}` | **상세 기록 수정** | `record_id` + Bearer Token + 수정 데이터 | 수정된 상세 기록 정보 |
| `DELETE` | `/records/{record_id}` | 기록 삭제 | `record_id` + Bearer Token | 삭제 확인 메시지 |

#### 📝 상세 기록 수정 (`PUT /records/{record_id}`)

**모든 타입의 상세기록을 수정할 수 있습니다:**
- 착유 기록, 사료급여 기록, 건강검진 기록, 체중측정 기록
- 백신접종 기록, 치료 기록, 발정 기록, 인공수정 기록
- 임신감정 기록, 분만 기록, 기타 모든 상세 기록

**수정 방법:**
- **기본 정보 수정**: `title`, `description`, `record_date`
- **상세 정보 수정**: `record_data` 객체 내의 특정 필드들
- **선택적 업데이트**: 입력한 필드만 수정되고 나머지는 기존 값 유지

**분만기록 수정 예시:**
```json
PUT /records/{record_id}
{
  "title": "분만 완료 (수정됨)",
  "record_data": {
    "calf_count": 2,
    "calving_difficulty": "약간어려움",
    "notes": "수정된 특이사항"
  }
}
```

**건강검진기록 수정 예시:**
```json
PUT /records/{record_id}
{
  "record_date": "2024-01-16",
  "record_data": {
    "body_temperature": 38.7,
    "heart_rate": 72,
    "notes": "정상 범위 내 수치 확인"
  }
}
```

### 📊 통계 및 분석 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/records/cow/{cow_id}/milking/statistics` | 착유 통계 | `cow_id` + Bearer Token | 일별 착유량, 평균값, 유성분 분석 |
| `GET` | `/records/cow/{cow_id}/weight/trend` | 체중 변화 추이 | `cow_id` + Bearer Token | 기간별 체중 증감 데이터 |
| `GET` | `/records/cow/{cow_id}/reproduction/timeline` | 번식 타임라인 | `cow_id` + Bearer Token | 발정, 수정, 임신, 분만 이력 |
| `GET` | `/records/cow/{cow_id}/summary` | 젖소 기록 요약 | `cow_id` + Bearer Token | 젖소별 기록 현황 요약 |

### 🔍 등록되어 있는 젖소의 상세 정보 기록 API

#### 카테고리별 기록 조회
| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/records/cow/{cow_id}/health-records` | 건강 기록 조회 | `cow_id` + Bearer Token | 건강검진, 백신, 치료 기록 |
| `GET` | `/records/cow/{cow_id}/milking-records` | 착유 기록 조회 | `cow_id` + Bearer Token | 모든 착유 기록 |
| `GET` | `/records/cow/{cow_id}/breeding-records` | 번식 기록 조회 | `cow_id` + Bearer Token | 발정, 수정, 임신, 분만 기록 |
| `GET` | `/records/cow/{cow_id}/feed-records` | 사료급여 기록 조회 | `cow_id` + Bearer Token | 모든 사료급여 기록 |
| `GET` | `/records/cow/{cow_id}/weight-records` | 체중측정 기록 조회 | `cow_id` + Bearer Token | 모든 체중측정 기록 |
| `GET` | `/records/cow/{cow_id}/all-records` | 전체 기록 조회 | `cow_id` + Bearer Token | 젖소의 모든 상세 기록 |

### 📊 기본 기록 관리 API (`/basic-records`)

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/basic-records/breeding` | 번식기록 생성 | `cow_id`, `record_date`, `title`, `breeding_method`, `breeding_date` | 생성된 번식기록 |
| `POST` | `/basic-records/disease` | 질병기록 생성 | `cow_id`, `record_date`, `title`, `disease_name` | 생성된 질병기록 |
| `POST` | `/basic-records/status-change` | 분류변경 기록 생성 | `cow_id`, `record_date`, `title`, `previous_status`, `new_status`, `change_reason`, `change_date` | 생성된 분류변경 기록 |
| `POST` | `/basic-records/other` | 기타기록 생성 | `cow_id`, `record_date`, `title` | 생성된 기타기록 |
| `GET` | `/basic-records/cow/{cow_id}` | 젖소별 기본 기록 조회 | `cow_id` + Bearer Token | 특정 젖소의 기본 기록 목록 |
| `GET` | `/basic-records/` | 농장 전체 기본 기록 조회 | Bearer Token | 농장의 모든 기본 기록 목록 |
| `GET` | `/basic-records/{record_id}` | 기본 기록 상세 조회 | `record_id` + Bearer Token | 특정 기본 기록의 상세 정보 |
| `PUT` | `/basic-records/{record_id}` | 기본 기록 업데이트 | `record_id` + Bearer Token | 업데이트된 기본 기록 |
| `DELETE` | `/basic-records/{record_id}` | 기본 기록 삭제 | `record_id` + Bearer Token | 삭제 확인 메시지 |
| `GET` | `/basic-records/recent/summary` | 최근 기록 조회 (홈화면용) | Bearer Token | 최근 기본 기록 목록 |
| `GET` | `/basic-records/statistics/summary` | 기본 기록 통계 | Bearer Token | 기록 유형별 통계 정보 |

### 🔗 축산물이력제 연동 API (`/api/livestock-trace`)

#### 인증 필요 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/api/livestock-trace/livestock-trace/{ear_tag_number}` | 축산물이력정보 전체 조회 | `ear_tag_number` + Bearer Token | 전체 이력정보 (기본정보, 농장이력, 도축정보, 백신정보 등) |
| `GET` | `/api/livestock-trace/livestock-quick-check/{ear_tag_number}` | 기본정보 빠른 확인 | `ear_tag_number` + Bearer Token | 기본 개체정보만 빠른 조회 |
| `POST` | `/api/livestock-trace/livestock-trace-async/{ear_tag_number}` | 비동기 전체정보 조회 | `ear_tag_number` + Bearer Token | task_id 반환 (백그라운드 처리) |
| `GET` | `/api/livestock-trace/livestock-trace-status/{task_id}` | 비동기 조회 상태 확인 | `task_id` + Bearer Token | 진행상황 및 결과 |

#### 개발/테스트용 API (인증 불필요)

| Method | Endpoint | 설명 | 응답 |
|--------|----------|------|------|
| `GET` | `/api/livestock-trace/test-quick-check-no-auth/{ear_tag_number}` | **테스트용 빠른 기본정보 확인** | 기본 개체정보 |
| `POST` | `/api/livestock-trace/test-async-no-auth/{ear_tag_number}` | **테스트용 비동기 전체 조회** | task_id |
| `GET` | `/api/livestock-trace/test-status-no-auth/{task_id}` | **테스트용 작업 상태 확인** | 진행상황 및 결과 |
| `GET` | `/api/livestock-trace/test-no-auth/{ear_tag_number}` | **테스트용 축산물이력정보 조회** | 전체 이력정보 |
| `GET` | `/api/livestock-trace/test-basic-no-auth/{ear_tag_number}` | **테스트용 기본 정보 조회** | 기본 개체정보 |

#### 축산물이력제 조회 정보

**기본 개체정보 (optionNo=1)**
- 개체번호, 이표번호, 출생일, 품종, 성별
- 개월령 자동계산, 수입경과월, 수입국가
- 농장식별번호, 농장번호
- 럼피스킨 최종접종일

**농장 등록 정보 (optionNo=2)**
- 사육지 주소, 농장경영자명
- 신고구분, 신고년월일, 농장번호
- 여러 농장 이동 이력 추적

**도축 정보 (optionNo=3)**
- 도축장 주소/명, 도축일자
- 등급, 근내지방도, 위생검사 결과

**포장 정보 (optionNo=4)**
- 포장처리업소 주소/명

**구제역 백신 정보 (optionNo=5)**
- 구제역 백신접종경과일/접종일/접종차수

**질병 정보 (optionNo=6)**
- 질병유무 상태

**브루셀라/결핵 검사 정보 (optionNo=7)**
- 브루셀라: 검사일, 결과, 경과일 자동계산
- 결핵: 검사일, 결과

#### 축산물이력제 연동 예시

```javascript
// 1. 기본정보 빠른 확인
GET /api/livestock-trace/livestock-quick-check/002123456789

// 2. 전체 이력정보 비동기 조회
POST /api/livestock-trace/livestock-trace-async/002123456789
// 응답: { "task_id": "task-uuid-123" }

// 3. 조회 상태 확인
GET /api/livestock-trace/livestock-trace-status/task-uuid-123
// 응답: {
//   "status": "processing",  // "processing" | "completed" | "failed"
//   "progress": 57,         // 0-100
//   "data": { ... }        // 완료 시 전체 데이터
// }

// 4. 전체 이력정보 동기 조회 (대기 시간 길어질 수 있음)
GET /api/livestock-trace/livestock-trace/002123456789
```

#### 응답 데이터 예시

```json
{
  "success": true,
  "message": "축산물이력정보 조회 완료",
  "ear_tag_number": "002123456789",
  "basic_info": {
    "cattle_no": "KR123456789",
    "ear_tag_number": "002123456789",
    "birth_date": "2022-03-15",
    "age_months": 22,
    "breed": "홀스타인",
    "gender": "암",
    "farm_unique_no": "1234567",
    "farm_no": "12345",
    "lumpy_skin_last_vaccination": "2024-01-15"
  },
  "farm_registrations": [
    {
      "farm_address": "경기도 OO시 XX구",
      "farmer_name": "홍길동",
      "registration_type": "출생",
      "registration_date": "2022-03-15",
      "farm_no": "12345"
    }
  ],
  "vaccination_info": {
    "fmd_injection_days": "45",
    "fmd_injection_date": "2023-12-01",
    "fmd_vaccine_order": "3"
  },
  "brucella_info": {
    "brucella_inspection_date": "2024-01-10",
    "brucella_result": "음성",
    "brucella_days_elapsed": 17
  }
}
```

### 🤖 AI 챗봇 API (`/chatbot`) - ⭐ 핵심 기능

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/chatbot/ask` | **챗봇 질문하기** | `user_id`, `chat_id`, `question` | `answer` |
| `GET` | `/chatbot/rooms/{user_id}` | **사용자 채팅방 목록 조회** | `user_id` (경로) | `chats: [{chat_id, created_at}]` |
| `POST` | `/chatbot/rooms` | **새로운 채팅방 생성** | `user_id` | `chats: [{chat_id, created_at}]` |
| `GET` | `/chatbot/history/{chat_id}` | **채팅방 대화 이력 조회** | `chat_id` (경로) | `chat_id`, `messages: [{role, content, timestamp}]` |
| `DELETE` | `/chatbot/rooms/{chat_id}` | **채팅방 및 메시지 삭제** | `chat_id` (경로) | `detail: 삭제 결과 메시지` |
| `DELETE` | `/chatbot/rooms/expired/auto` | **14일 이상된 채팅방 자동 삭제** | 없음 | `detail: 삭제 결과 메시지` |

#### 🤖 AI 챗봇 "소담이" 상세 기능

**소담이의 특징:**
- **이름**: 소담이 (낙농업 전문 AI 어시스턴트)
- **AI 엔진**: OpenAI GPT-4o-mini
- **프레임워크**: LangGraph 기반 고급 대화 플로우 관리
- **언어 지원**: 한국어 전용 (낙농업 전문용어 특화)

**질문 자동 분류 시스템:**

소담이는 사용자의 질문을 다음 4가지로 자동 분류하여 최적의 응답을 제공합니다:

1. **rag (낙농 지식 질문)**
   - 낙농업 관련 전문 정보, 기술, 정책, 용어 등
   - 예시: "젖소의 발정 주기는?", "착유기는 어떻게 작동하나요?", "낙농업 역사 알려줘"

2. **cow_info (농장 데이터 질문)**
   - 사용자의 농장에 등록된 소 정보나 상태, 기록 등
   - 예시: "103번 소 상태 알려줘", "어제 분만한 소들 누구야?", "이표번호 002123456789 소 정보"

3. **general (일반 대화)**
   - 챗봇 자체에 대한 질문, 인사, 감정 표현, 잡담 등
   - 예시: "안녕", "이전 질문 뭐였지?", "소담이 귀엽다", "고마워", "너 누구야?"

4. **irrelevant (무관한 질문)**
   - 낙농업 또는 사용자의 목장과 완전히 무관한 질문
   - 예시: "로또 번호 알려줘", "요즘 주식 어때요?", "오늘 점심 뭐 먹지?"

**AI 챗봇 사용 방법:**

```javascript
// 1. 새 채팅방 생성
POST /chatbot/rooms
{
  "user_id": "user123"
}

// 2. 질문하기
POST /chatbot/ask
{
  "user_id": "user123",
  "chat_id": "chat-uuid-123",
  "question": "젖소 발정 증상이 뭔가요?"
}

// 3. 대화 이력 조회
GET /chatbot/history/chat-uuid-123

// 4. 사용자의 모든 채팅방 조회
GET /chatbot/rooms/user123
```

**AI 챗봇 응답 예시:**

- **낙농 지식 질문**: "젖소의 발정 주기는 평균 21일입니다. 발정 증상으로는 다른 소에게 올라타거나, 불안해하며 울음소리를 내는 행동을 보입니다..."

- **농장 데이터 질문**: "꽃분이(002123456789) 소의 최근 착유 기록: 착유량 25.5L, 1회차, 유지방 3.8% (날짜: 2025-06-27)"

- **일반 대화**: "안녕하세요! 저는 낙농업 도우미 소담이예요. 젖소 관리나 낙농업에 관한 궁금한 점이 있으시면 언제든 물어보세요!"

### 🔧 시스템 정보 API

| Method | Endpoint | 설명 | 응답 |
|--------|----------|------|------|
| `GET` | `/` | 서버 정보 및 상태 | 서버 버전, 환경, 기능 목록 |
| `GET` | `/health` | 헬스 체크 | 서버 상태, 버전, Swagger UI 정보 |

### 🛠️ 개발 환경 전용 API

**로컬 개발 환경에서만 사용 가능** (`ENVIRONMENT=development`)

| Method | Endpoint | 설명 | 응답 |
|--------|----------|------|------|
| `GET` | `/docs` | Swagger UI | 인터랙티브 API 문서 |
| `GET` | `/redoc` | ReDoc | 대안 API 문서 |
| `GET` | `/openapi.json` | OpenAPI 스키마 | JSON 형태의 API 스키마 |
| `GET` | `/openapi-download` | OpenAPI 다운로드 | 다운로드 가능한 JSON 파일 |

### 📢 알림 시스템 API (`/api/notifications`) - NEW!

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/api/notifications/create` | **알림 생성** | `user_id`, `notification_type`, `title`, `message` + Bearer Token | 생성된 알림 정보 |
| `GET` | `/api/notifications/` | **알림 목록 조회** | Bearer Token | 필터링된 알림 목록 |
| `GET` | `/api/notifications/unread` | **읽지 않은 알림 조회** | Bearer Token | 읽지 않은 알림만 |
| `GET` | `/api/notifications/{id}` | **알림 상세 조회** | `id` + Bearer Token | 특정 알림 상세 정보 |
| `PATCH` | `/api/notifications/{id}/read` | **알림 읽음 처리** | `id` + Bearer Token | 읽음 처리된 알림 |
| `PATCH` | `/api/notifications/read-all` | **모든 알림 읽음 처리** | Bearer Token | 처리 결과 |
| `DELETE` | `/api/notifications/{id}` | **알림 삭제** | `id` + Bearer Token | 삭제 확인 메시지 |
| `GET` | `/api/notifications/statistics` | **알림 통계 조회** | Bearer Token | 통계 정보 |
| `GET` | `/api/notifications/settings` | **알림 설정 조회** | Bearer Token | 사용자 알림 설정 |
| `PUT` | `/api/notifications/settings` | **알림 설정 업데이트** | Bearer Token | 업데이트된 설정 |

#### 🔥 FCM 푸시 알림 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/api/notifications/fcm/token` | **FCM 토큰 등록** | `fcm_token` + Bearer Token | 등록 확인 메시지 |
| `DELETE` | `/api/notifications/fcm/token` | **FCM 토큰 삭제** | Bearer Token | 삭제 확인 메시지 |
| `POST` | `/api/notifications/fcm/topic/{topic}/subscribe` | **토픽 구독** | `topic` + Bearer Token | 구독 확인 메시지 |
| `DELETE` | `/api/notifications/fcm/topic/{topic}/unsubscribe` | **토픽 구독 해제** | `topic` + Bearer Token | 해제 확인 메시지 |

#### 📋 관리자용 알림 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/api/notifications/batch` | **일괄 알림 발송** | `user_ids`, `notification_type`, `title`, `message` + Bearer Token | 발송 결과 |
| `POST` | `/api/notifications/test` | **알림 테스트** | Bearer Token | 테스트 알림 |

#### 알림 시스템 특징
- ✅ **다중 채널 지원** - 앱 내 알림, 이메일, 푸시 알림
- ✅ **자동 알림** - 할일 마감, 지연, 일일/주간 요약 자동 발송
- ✅ **수동 알림** - 관리자가 직접 알림 생성 및 일괄 발송
- ✅ **FCM 푸시 알림** - Firebase Cloud Messaging 기반 실시간 푸시
- ✅ **알림 설정** - 사용자별 채널/유형/시간대 설정
- ✅ **통계 및 분석** - 알림 발송 현황 및 사용자 반응 분석

#### 알림 생성 예시

```json
POST /api/notifications/create
{
  "user_id": "user-uuid",
  "notification_type": "task_due_soon",
  "title": "할일 마감 임박",
  "message": "'103번 소 건강검진' 할일이 1시간 후 마감됩니다.",
  "priority": "high",
  "channels": ["in_app", "push"],
  "related_task_id": "task-uuid",
  "scheduled_at": "2025-07-05T08:00:00Z"
}
```

#### FCM 토큰 등록 예시

```json
POST /api/notifications/fcm/token
{
  "fcm_token": "fcm_token_from_flutter_app"
}
```

#### 일괄 알림 발송 예시 (관리자용)

```json
POST /api/notifications/batch
{
  "user_ids": ["user1", "user2", "user3"],
  "farm_id": "farm-uuid",
  "notification_type": "system_maintenance",
  "title": "시스템 점검 알림",
  "message": "오늘 밤 12시부터 2시간 동안 시스템 점검이 예정되어 있습니다.",
  "priority": "high",
  "channels": ["in_app", "push", "email"]
}
```

#### 알림 통계 응답 예시

```json
{
  "total_notifications": 150,
  "unread_notifications": 25,
  "read_notifications": 125,
  "today_notifications": 8,
  "by_type": {
    "task_due_soon": 45,
    "system_maintenance": 12,
    "cow_registered": 23,
    "milking_record_created": 70
  },
  "by_priority": {
    "low": 30,
    "medium": 80,
    "high": 35,
    "urgent": 5
  },
  "by_status": {
    "unread": 25,
    "read": 125
  }
}
```

### 🔥 Firebase Cloud Messaging (FCM) 설정 가이드

#### 1️⃣ Firebase 콘솔 설정

1. **Firebase 프로젝트 설정**
   - [Firebase Console](https://console.firebase.google.com/) 접속
   - 기존 프로젝트 선택 또는 새 프로젝트 생성
   - **Cloud Messaging** 메뉴로 이동

2. **서버 키 생성**
   - **프로젝트 설정** → **Cloud Messaging** 탭
   - **서버 키** 생성 (백엔드에서 사용)

3. **서비스 계정 키 파일 다운로드**
   - **프로젝트 설정** → **서비스 계정** 탭
   - **새 비공개 키 생성** → JSON 파일 다운로드
   - 파일을 `backend/firebase-adminsdk.json`으로 저장

#### 2️⃣ 백엔드 환경 설정

```bash
# 필요한 패키지 설치
pip install firebase-admin

# .env 파일에 추가
FIREBASE_ADMIN_SDK_PATH=firebase-adminsdk.json
```

#### 3️⃣ Flutter 앱에서 FCM 토큰 등록

```dart
// Flutter 앱에서 FCM 토큰을 백엔드에 등록
Future<void> registerFCMToken() async {
  String? fcmToken = await FirebaseMessaging.instance.getToken();
  
  if (fcmToken != null) {
    final response = await http.post(
      Uri.parse('$baseUrl/api/notifications/fcm/token'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
      body: json.encode({'fcm_token': fcmToken}),
    );
    
    if (response.statusCode == 200) {
      print('FCM 토큰 등록 성공');
    }
  }
}
```

#### 4️⃣ 알림 유형 (실제 구현된 것만)

##### �� 할일 관련 알림
- `TASK_DUE_SOON` - 할일 마감 임박 (1시간 전)
- `TASK_OVERDUE` - 할일 지연
- `TASK_COMPLETED` - 할일 완료
- `TASK_CREATED` - 할일 생성
- `TASK_ASSIGNED` - 할일 배정

##### 🐮 젖소 관리 알림
- `COW_REGISTERED` - 젖소 등록 완료
- `COW_UPDATED` - 젖소 정보 수정
- `COW_DELETED` - 젖소 삭제
- `COW_FAVORITE_ADDED/REMOVED` - 즐겨찾기 추가/제거

##### 🔗 축산물이력제 알림
- `LIVESTOCK_TRACE_SUCCESS` - 축산물이력제 조회 성공
- `LIVESTOCK_TRACE_FAILED` - 축산물이력제 조회 실패
- `LIVESTOCK_TRACE_ALREADY_REGISTERED` - 이미 등록된 젖소

##### �� 기록 관리 알림
- `RECORD_CREATED` - 기록 생성
- `RECORD_UPDATED` - 기록 수정
- `RECORD_DELETED` - 기록 삭제
- `RECORD_MISSING` - 기록 누락

##### �� 건강 관리 알림
- `HEALTH_CHECK_DUE` - 건강검진 예정
- `HEALTH_CHECK_COMPLETED` - 건강검진 완료
- `VACCINATION_DUE` - 백신 접종 예정
- `VACCINATION_COMPLETED` - 백신 접종 완료
- `TREATMENT_STARTED` - 치료 시작
- `TREATMENT_COMPLETED` - 치료 완료

##### 🥛 착유 관련 알림
- `MILKING_RECORD_CREATED` - 착유 기록 생성
- `MILKING_YIELD_LOW` - 착유량 저하
- `MILKING_YIELD_HIGH` - 착유량 증가
- `MILKING_MISSED` - 착유 누락
- `MILKING_QUALITY_ISSUE` - 착유 품질 문제

##### �� 번식 관리 알림
- `ESTRUS_DETECTED` - 발정 감지
- `INSEMINATION_SCHEDULED` - 인공수정 예정
- `PREGNANCY_CHECK_DUE` - 임신감정 예정
- `CALVING_PREDICTED` - 분만 예정
- `CALVING_COMPLETED` - 분만 완료

##### �� 사료 관리 알림
- `FEED_SCHEDULE_REMINDER` - 사료 급여 일정
- `FEED_RECORD_CREATED` - 사료 급여 기록
- `FEED_QUALITY_ISSUE` - 사료 품질 문제
- `FEED_SHORTAGE` - 사료 부족

##### ⚖️ 체중 관리 알림
- `WEIGHT_MEASUREMENT_DUE` - 체중 측정 예정
- `WEIGHT_ABNORMAL` - 체중 이상
- `WEIGHT_TARGET_REACHED` - 목표 체중 달성

##### 🔍 검사 관련 알림
- `BRUCELLA_TEST_DUE` - 브루셀라 검사 예정
- `BRUCELLA_TEST_RESULT` - 브루셀라 검사 결과
- `TUBERCULOSIS_TEST_DUE` - 결핵 검사 예정
- `TUBERCULOSIS_TEST_RESULT` - 결핵 검사 결과

##### ��️ 시스템 알림
- `SYSTEM_MAINTENANCE` - 시스템 점검
- `SECURITY_ALERT` - 보안 알림
- `WELCOME` - 환영 알림
- `ACCOUNT_CREATED/UPDATED` - 계정 생성/수정
- `PASSWORD_CHANGED` - 비밀번호 변경
- `LOGIN_ATTEMPT/FAILED/SUCCESS` - 로그인 관련

##### 📊 통계 알림
- `DAILY_SUMMARY` - 일일 요약
- `WEEKLY_SUMMARY` - 주간 요약
- `MONTHLY_SUMMARY` - 월간 요약
- `PERFORMANCE_ALERT` - 성과 알림
- `TREND_ANALYSIS` - 트렌드 분석

#### 5️⃣ 자동 알림 스케줄러

- **할일 마감 임박 알림**: 매 30분마다 체크, 마감 1시간 전 발송
- **지연된 할일 알림**: 매시간 체크, 마감일 지난 할일 발송
- **일일 요약 알림**: 매일 오전 9시, 오늘 할일 현황 발송
- **주간 요약 알림**: 매주 월요일 오전 9시, 주간 통계 발송

#### 6️⃣ 알림 설정 관리

사용자는 다음 설정을 개별적으로 관리할 수 있습니다:

- **채널별 설정**: 앱 내, 이메일, 푸시 알림 on/off
- **유형별 설정**: 할일, 젖소, 기록, 시스템 등 카테고리별 on/off
- **시간대 설정**: 방해 금지 시간 설정 (예: 22:00~08:00)
- **우선순위 설정**: 긴급/높음/보통/낮음 알림별 수신 여부

## 🔗 축산물이력제 연동 등록 플로우

### 3단계 젖소 등록 프로세스

```
                        1단계: 이표번호 입력
                                  ↓
              GET /cows/registration-status/{ear_tag_number}
                                  ↓
        ┌─────────────────────────┼─────────────────────────┐
        ↓                         ↓                         ↓
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ already_registered │ │ livestock_trace_  │  │manual_registration│
│                   │  │    available      │  │     _required     │
│                   │  │                   │  │                   │
│ 이미 등록된 젖소  │  │  축산물이력제에서 │  │  축산물이력제에서 │
│    (등록 불가)    │  │     정보 찾음     │  │     정보 없음     │
│                   │  │                   │  │                   │
│  ❌ 오류 메시지  │  │         ↓         │  │         ↓         │
│                   │  │                   │  │                   │
│                   │  │ POST /cows/       │  │ POST /cows/manual │
│                   │  │ register-from-    │  │                   │
│                   │  │ livestock-trace   │  │                   │
│                   │  │                   │  │                   │
│                   │  │(축산물이력제 기반 │  │ (사용자 직접 입력 │
│                   │  │     자동 등록)    │  │    수동 등록)     │
└───────────────────┘  └─────────┬─────────┘  └─────────┬─────────┘
                                 ↓                      ↓
                                 └──────────┬───────────┘
                                            ↓
                                       등록 완료 성공
                                            ↓
                                       GET /cows/
                                     (젖소 목록 조회)
```

### 축산물이력제 조회 정보

**기본 개체정보 (optionNo=1)**
- 개체번호, 이표번호, 출생일, 품종, 성별
- 개월령 자동계산, 수입경과월, 수입국가
- 농장식별번호, 농장번호
- 럼피스킨 최종접종일

**농장 등록 정보 (optionNo=2)**
- 사육지 주소, 농장경영자명
- 신고구분, 신고년월일, 농장번호
- 여러 농장 이동 이력 추적

**도축 정보 (optionNo=3)**
- 도축장 주소/명, 도축일자
- 등급, 근내지방도, 위생검사 결과

**포장 정보 (optionNo=4)**
- 포장처리업소 주소/명

**구제역 백신 정보 (optionNo=5)**
- 구제역 백신접종경과일/접종일/접종차수

**질병 정보 (optionNo=6)**
- 질병유무 상태

**브루셀라/결핵 검사 정보 (optionNo=7)**
- 브루셀라: 검사일, 결과, 경과일 자동계산
- 결핵: 검사일, 결과

## 🤖 AI 챗봇 "소담이" 기술 상세

### LangGraph 기반 대화 플로우

소담이는 최신 LangGraph 기술을 사용하여 지능형 대화 플로우를 구현합니다:

```python
# 대화 플로우 예시
user_question -> 질문_분류 -> 
┌─ rag: 낙농 지식 검색 + RAG 응답
├─ cow_info: 농장 데이터 조회 + 맞춤 응답  
├─ general: 일반 대화 응답
└─ irrelevant: 안내 메시지
```

### 질문 분류 시스템

**자동 분류 로직:**
1. **의도 분석**: 사용자 질문의 의도를 파악
2. **키워드 매칭**: 낙농업 전문용어 및 농장 데이터 키워드 감지
3. **컨텍스트 이해**: 이전 대화 맥락 고려
4. **최적 경로 선택**: 4가지 응답 경로 중 최적 선택

### 농장 데이터 연동

**이표번호 인식:**
- 12자리 숫자 패턴 자동 인식
- 사용자 농장의 젖소 정보 실시간 조회
- 기록 유형별 필터링 (착유, 발정, 건강 등)

**예시 질문과 응답:**
```
사용자: "002123456789번 소 어제 착유량 어땠어?"
소담이: "꽃분이(002123456789) 소의 최근 착유 기록을 확인해드릴게요. 
        어제 착유량은 24.2L이고, 유지방 3.9%, 유단백 3.1%였습니다."
```

### 메모리 관리

**대화 맥락 유지:**
- 채팅방별 대화 이력 저장
- 이전 질문-답변 참조 가능
- 연속적인 대화 플로우 지원

**자동 정리:**
- 14일 이상된 채팅방 자동 삭제
- 메모리 최적화 관리

## 📚 API 문서 및 개발 도구

### 🔧 로컬 개발환경에서 Swagger UI 사용

로컬 개발 시에는 Swagger UI를 활용하여 API를 쉽게 테스트할 수 있습니다.

```bash
# 개발 환경으로 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**로컬 개발 시 접속 가능한 문서:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **OpenAPI 다운로드**: http://localhost:8000/openapi-download

## 🧪 API 테스트

> **⚠️ 중요**: AWS EC2 사용량 절약을 위해 프로덕션에서는 Swagger UI가 비활성화되어 있습니다. curl 명령어나 Postman을 사용하여 API를 테스트하세요.

### AI 챗봇 테스트 예시

```bash
# 1. 새 채팅방 생성
curl -X POST "http://localhost:8000/chatbot/rooms" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'

# 2. 낙농 지식 질문
curl -X POST "http://localhost:8000/chatbot/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "chat_id": "chat_uuid_123",
    "question": "젖소 발정 증상이 뭔가요?"
  }'

# 3. 농장 데이터 질문 (이표번호 포함)
curl -X POST "http://localhost:8000/chatbot/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user", 
    "chat_id": "chat_uuid_123",
    "question": "002123456789번 소 최근 착유량 알려줘"
  }'

# 4. 대화 이력 조회
curl -X GET "http://localhost:8000/chatbot/history/chat_uuid_123"
```

### Task Management API 테스트 예시

```bash
# 1. 새 작업 생성
curl -X POST "http://localhost:8000/api/todos" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "젖소 건강검진",
    "description": "전체 젖소 대상 정기 건강검진 실시",
    "due_date": "2024-02-15",
    "priority": "high",
    "category": "health_check",
    "assigned_to": ["user123", "user456"],
    "related_cows": ["cow123", "cow456"]
  }'

# 2. 작업 목록 필터링
curl -X GET "http://localhost:8000/api/todos/filter?status=pending&priority=high" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 작업 상태 변경
curl -X PATCH "http://localhost:8000/api/todos/task_123/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "status": "completed",
    "completion_notes": "모든 젖소 건강검진 완료"
  }'

# 4. 작업 상세 조회
curl -X GET "http://localhost:8000/api/todos/task_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 설치 및 실행

### 환경 요구사항
- **Python**: 3.11 이상
- **Firebase**: Firestore 데이터베이스
- **축산물이력제**: 축산물품질평가원 OpenAPI 키
- **OpenAI**: GPT-4o-mini API 키 (챗봇 기능)

### 1️⃣ 프로젝트 설정

```bash
# 레포지토리 클론
git clone https://github.com/BlackCows-Team/blackcows-server.git
cd blackcows-server

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ 환경변수 설정

```bash
# .env 파일 생성
JWT_SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LIVESTOCK_TRACE_API_DECODING_KEY=your_livestock_api_key
OPENAI_API_KEY=your_openai_api_key  # AI 챗봇용
```

### 3️⃣ 서버 실행

```bash
# 개발 서버 실행 (Swagger UI 포함)
ENVIRONMENT=development uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버 실행 (Swagger UI 비활성화)
ENVIRONMENT=production uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 데이터베이스 구조

### 🐮 젖소 정보 컬렉션: `cows`
```json
{
  "id": "uuid",
  "ear_tag_number": "012345678912",
  "name": "꽃분이",
  "birthdate": "2022-03-15",
  "sensor_number": "1234567890123",
  "health_status": "normal",
  "breeding_status": "lactating",
  "breed": "Holstein",
  "notes": "우수한 젖소",
  "is_favorite": true,
  "farm_id": "farm_uuid",
  "owner_id": "user_uuid",
  "has_detailed_info": true,
  "detailed_info": {
    "body_info": {
      "weight": 450.5,
      "body_condition_score": 3.5
    },
    "management_info": {
      "purchase_price": 2500000,
      "barn_section": "A동"
    }
  },
  "livestock_trace_data": {
    "basic_info": {
      "cattle_no": "KR123456789",
      "birth_date": "2022-03-15",
      "breed": "홀스타인",
      "gender": "암컷"
    }
  },
  "registered_from_livestock_trace": true,
  "livestock_trace_registered_at": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

### 🤖 AI 챗봇 데이터 구조

#### 채팅방 컬렉션: `chat_rooms`
```json
{
  "chat_id": "uuid",
  "user_id": "user_uuid", 
  "created_at": "timestamp"
}
```

#### 메시지 서브컬렉션: `chat_rooms/{chat_id}/messages`
```json
{
  "role": "user|assistant",
  "content": "메시지 내용",
  "timestamp": "timestamp"
}
```

### 📝 상세 기록 컬렉션: `cow_detailed_records`
```json
{
  "id": "uuid",
  "cow_id": "cow_uuid",
  "record_type": "milking",
  "record_date": "2025-06-22",
  "title": "착유 기록 (25.5L, 1회차)",
  "description": "유지방 3.8%, 유단백 3.2%, 체세포수 150,000",
  "record_data": {
    "milk_yield": 25.5,
    "milking_session": 1,
    "milking_start_time": "06:00:00",
    "milking_end_time": "06:20:00",
    "fat_percentage": 3.8,
    "protein_percentage": 3.2,
    "somatic_cell_count": 150000,
    "temperature": 37.5,
    "conductivity": 5.2,
    "blood_flow_detected": false,
    "color_value": "정상",
    "air_flow_value": 2.1,
    "lactation_number": 3,
    "rumination_time": 480,
    "collection_code": "AUTO",
    "collection_count": 1,
    "notes": null
  },
  "farm_id": "farm_uuid",
  "owner_id": "user_uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

### 📊 기본 기록 컬렉션: `cow_records`
```json
{
  "id": "uuid",
  "cow_id": "cow_uuid",
  "record_type": "breeding",
  "record_date": "2025-06-22",
  "title": "인공수정 실시",
  "description": "홀스타인 정액 사용",
  "record_data": {
    "breeding_method": "artificial",
    "breeding_date": "2025-06-22",
    "bull_info": "홀스타인 우수 종축",
    "expected_calving_date": "2026-03-30",
    "breeding_result": "pending",
    "cost": 50000,
    "veterinarian": "김수의사"
  },
  "farm_id": "farm_uuid",
  "owner_id": "user_uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

### 👥 사용자 정보 컬렉션: `users`
```json
{
  "id": "uuid",
  "username": "홍길동",
  "user_id": "admin123",
  "email": "admin@farm.com",
  "farm_nickname": "행복농장",
  "farm_id": "farm_uuid",
  "hashed_password": "bcrypt_hash",
  "is_active": true,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 🏢 농장 정보 컬렉션: `farms`
```json
{
  "farm_id": "farm_uuid",
  "farm_nickname": "행복농장",
  "owner_id": "user_uuid",
  "owner_name": "홍길동",
  "owner_user_id": "admin123",
  "created_at": "timestamp",
  "is_active": true
}
```

### 📋 작업 관리 컬렉션: `tasks`
```json
{
  "id": "task_uuid",
  "title": "젖소 건강검진",
  "description": "전체 젖소 대상 정기 건강검진 실시",
  "status": "pending",
  "priority": "high",
  "category": "health_check",
  "due_date": "2024-02-15",
  "created_at": "2024-01-27T09:00:00Z",
  "updated_at": "2024-01-27T09:00:00Z",
  "created_by": "user_uuid",
  "farm_id": "farm_uuid",
  "assigned_to": ["user123", "user456"],
  "related_cows": ["cow123", "cow456"],
  "completion_date": null,
  "completion_notes": null,
  "attachments": [
    {
      "id": "attachment_uuid",
      "filename": "health_report.pdf",
      "url": "https://storage.example.com/files/health_report.pdf",
      "uploaded_at": "2024-01-27T09:05:00Z"
    }
  ],
  "tags": ["정기검진", "전체"],
  "is_active": true
}
```

## 🔐 인증 및 보안

### JWT 토큰 시스템
- **Access Token**: 30분 만료, API 호출에 사용
- **Refresh Token**: 7일 만료, Access Token 갱신에 사용
- **Password Reset Token**: 1시간 만료, 비밀번호 재설정 전용
- **Password Reset Access Token**: 30분 만료, 비밀번호 변경 권한만

### 비밀번호 재설정 플로우
1. 사용자가 이름, 아이디, 이메일 입력
2. 서버에서 사용자 확인 후 JWT 토큰 생성
3. 이메일로 재설정 링크 발송
4. 사용자가 임시 토큰으로 로그인
5. 새 비밀번호로 변경
6. 모든 기존 리프레시 토큰 무효화

### 데이터 보안
- 농장별 데이터 완전 격리
- 소프트 삭제로 데이터 무결성 유지
- bcrypt 비밀번호 해싱
- Firebase Security Rules 적용
- 축산물이력제 API 키 보안 관리

## 🔗 축산물이력제 연동 상세

### API 연동 방식
- **기관**: 축산물품질평가원 (EKAPE)
- **API 타입**: REST API (XML 응답)
- **인증**: Service Key 기반
- **URL**: `http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch`

### 조회 옵션별 정보

| optionNo | 조회 정보 | 주요 데이터 |
|----------|-----------|-------------|
| 1 | 기본 개체정보 | 개체번호, 출생일, 품종, 성별, 개월령 |
| 2 | 농장 등록 정보 | 사육지, 농장경영자, 신고이력 |
| 3 | 도축 정보 | 도축장, 등급, 근내지방도 |
| 4 | 포장 정보 | 포장처리업소 |
| 5 | 구제역 백신 | 접종일, 차수, 경과일 |
| 6 | 질병 정보 | 질병유무 |
| 7 | 브루셀라/결핵 | 검사일, 결과, 경과일 |

## 📈 주요 업데이트 내역

### v2.9.0 (2025-07-10) - 알림 시스템 완전 구현

#### 🔥 FCM 푸시 알림 시스템 출시
- **Firebase Cloud Messaging 연동**: 실시간 푸시 알림 지원
- **다중 채널 발송**: 앱 내, 이메일, 푸시 알림 동시 발송
- **FCM 토큰 관리**: 사용자별 FCM 토큰 등록/삭제/관리
- **토픽 구독 시스템**: 특정 주제별 알림 구독/해제

#### 📢 알림 시스템 고도화
- **80개 이상 알림 유형**: 할일, 젖소, 기록, 시스템 등 모든 기능 연동
- **자동 스케줄러**: 할일 마감, 지연, 요약 알림 자동 발송
- **관리자 일괄 발송**: 다수 사용자 대상 공지/긴급 알림 발송
- **알림 설정 관리**: 사용자별 세부 설정 (채널/유형/시간대)

#### 🛠️ 관리자 기능 강화
- **토큰 관리 시스템**: 만료 토큰 자동 정리, 사용자별 토큰 무효화
- **시스템 모니터링**: 토큰 사용 현황, 알림 발송 통계
- **보안 강화**: 임시 비밀번호 정리, 관리자 권한 관리

#### 새로운 엔드포인트
- `POST /api/notifications/create`: 알림 생성
- `GET /api/notifications/`: 알림 목록 조회
- `PATCH /api/notifications/{id}/read`: 알림 읽음 처리
- `POST /api/notifications/fcm/token`: FCM 토큰 등록
- `POST /api/notifications/batch`: 일괄 알림 발송 (관리자용)
- `GET /admin/token-stats`: 토큰 통계 조회
- `POST /admin/cleanup-tokens`: 토큰 정리 실행

### v2.7.0 (2025-06-27) - 🤖 AI 챗봇 "소담이" 완전체 (NEW!)
#### 🤖 AI 챗봇 기능 완전 구현
- **LangGraph 기반 지능형 대화 시스템**: 고급 대화 플로우 및 상태 관리
- **4가지 질문 자동 분류**: 낙농 지식, 농장 데이터, 일반 대화, 무관한 질문
- **OpenAI GPT-4o-mini 엔진**: 최신 AI 모델로 정확하고 자연스러운 응답
- **한국어 전용 낙농업 특화**: 낙농업 전문용어와 농장 환경에 최적화
- **농장 데이터 실시간 연동**: 사용자의 젖소 정보와 기록을 활용한 맞춤형 답변
- **채팅방 관리 시스템**: 개별 대화방 생성, 이력 관리, 자동 정리
- **메모리 기반 연속 대화**: 대화 맥락을 유지하는 지능형 응답 시스템

#### 🔗 축산물이력제 연동 고도화
- **5분 캐싱 시스템**: API 응답 캐시로 성능 최적화
- **비동기 처리 강화**: 백그라운드 작업으로 사용자 경험 개선
- **오류 처리 개선**: 일부 API 실패 시에도 가용한 정보 수집 계속

#### 🔐 사용자 관리 기능 확장
- **목장 이름 수정**: 사용자가 직접 목장 이름 변경 가능
- **향상된 사용자 검증**: 이름과 이메일 기반 아이디 찾기 정확도 향상
- **보안 토큰 시스템**: JWT 기반 비밀번호 재설정 보안 강화

### v2.6.3 (2025-06-25)
#### 🤖 AI 챗봇 "소담이" 추가
- **LangGraph 기반 대화 시스템**: 고도화된 대화 플로우 관리
- **질문 자동 분류**: 낙농 지식, 농장 데이터, 일반 대화, 무관한 질문 자동 구분
- **OpenAI GPT-4o-mini**: 최신 AI 모델 활용으로 정확한 응답 제공
- **한국어 전용**: 낙농업 전문용어에 특화된 한국어 대화 지원
- API 엔드포인트 추가
  - POST    /chatbot/ask
  - GET     /chatbot/rooms/{user_id}
  - POST    /chatbot/rooms
  - GET     /chatbot/history/{chat_id}
  - DELETE  /chatbot/rooms/{chat_id}
  - DELETE  /chatbot/rooms/expired/auto 

#### 🔐 사용자 관리 기능 강화
- **목장 이름 수정 기능**: PUT /auth/update-farm-name 엔드포인트 추가
- **향상된 사용자 검증**: 이름과 이메일 기반 아이디 찾기 정확도 향상
- **보안 강화**: 토큰 기반 비밀번호 재설정 시스템 개선

#### 🔗 축산물이력제 연동 최적화
- **캐싱 시스템**: 5분간 API 응답 캐시로 성능 향상
- **테스트 엔드포인트 확장**: 개발자 친화적인 인증 불필요 테스트 API 추가
- **오류 처리 개선**: 일부 API 실패 시에도 나머지 정보 수집 계속 진행

### v2.6.0 (2025-06-22)
#### 🔗 축산물이력제 연동 기능 추가
- **젖소 등록 상태 확인**: `/cows/registration-status/{ear_tag_number}`
- **축산물이력제 기반 등록**: `/cows/register-from-livestock-trace`
- **3단계 등록 플로우**: 축산물이력제 우선 → 수동 등록 대안
- **전체 이력정보 조회**: 7개 옵션별 데이터 수집
- **비동기 처리**: 백그라운드 작업으로 성능 최적화

#### 📊 상세 기록 관리 시스템 확장
- **10가지 상세 기록 유형**: 착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료
- **카테고리별 조회 API**: 건강/번식/사료 등 카테고리별 필터링
- **통계 및 분석**: 착유 통계, 체중 변화 추이, 번식 타임라인
- **프론트엔드 전용 API**: Flutter 앱 최적화된 엔드포인트

#### 🔐 보안 및 인증 강화
- **비밀번호 재설정 개선**: JWT 기반 토큰 시스템
- **임시 토큰 로그인**: 비밀번호 변경 권한 분리
- **회원탈퇴**: 관련 데이터 완전 삭제
- **리프레시 토큰 관리**: 보안 강화된 토큰 무효화

### 새로운 엔드포인트 (v2.7.0)
#### AI 챗봇 완전체
- `POST /chatbot/ask`: **챗봇 질문하기** (LangGraph + 농장 데이터 연동)
- `GET /chatbot/rooms/{user_id}`: **사용자 채팅방 목록 조회**
- `POST /chatbot/rooms`: **새로운 채팅방 생성**
- `GET /chatbot/history/{chat_id}`: **채팅방 대화 이력 조회**
- `DELETE /chatbot/rooms/{chat_id}`: **채팅방 및 메시지 삭제**
- `DELETE /chatbot/rooms/expired/auto`: **14일 이상된 채팅방 자동 삭제**

#### 사용자 관리
- `PUT /auth/update-farm-name`: 목장 이름 수정

### 새로운 엔드포인트 (v2.6.0)
#### 축산물이력제 연동
- `GET /cows/registration-status/{ear_tag_number}`: 등록 상태 확인
- `POST /cows/register-from-livestock-trace`: 축산물이력제 기반 등록
- `GET /cows/{cow_id}/livestock-trace-info`: 축산물이력제 정보 조회
- `GET /api/livestock-trace/livestock-trace/{ear_tag_number}`: 전체 이력정보
- `GET /api/livestock-trace/livestock-quick-check/{ear_tag_number}`: 빠른 확인
- `POST /api/livestock-trace/livestock-trace-async/{ear_tag_number}`: 비동기 조회

#### 상세 기록 관리
- `POST /records/milking`: 착유 기록 생성
- `POST /records/estrus`: 발정 기록 생성
- `POST /records/insemination`: 인공수정 기록 생성
- `POST /records/pregnancy-check`: 임신감정 기록 생성
- `POST /records/calving`: 분만 기록 생성
- `POST /records/feed`: 사료급여 기록 생성
- `POST /records/health-check`: 건강검진 기록 생성
- `POST /records/vaccination`: 백신접종 기록 생성
- `POST /records/weight`: 체중측정 기록 생성
- `POST /records/treatment`: 치료 기록 생성

#### 통계 및 분석
- `GET /records/cow/{cow_id}/milking/statistics`: 착유 통계
- `GET /records/cow/{cow_id}/weight/trend`: 체중 변화 추이
- `GET /records/cow/{cow_id}/reproduction/timeline`: 번식 타임라인
- `GET /records/cow/{cow_id}/summary`: 젖소 기록 요약

#### 카테고리별 조회
- `GET /records/cow/{cow_id}/health-records`: 건강 기록
- `GET /records/cow/{cow_id}/breeding-records`: 번식 기록
- `GET /records/cow/{cow_id}/feed-records`: 사료급여 기록
- `GET /records/cow/{cow_id}/weight-records`: 체중측정 기록
- `GET /records/cow/{cow_id}/all-records`: 전체 기록

#### 인증 및 보안
- `POST /auth/login-with-reset-token`: 임시 토큰 로그인
- `POST /auth/change-password`: 비밀번호 변경
- `DELETE /auth/delete-account`: 회원탈퇴

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI 2.3.1 (Python 3.11+)
- **Database**: Firebase Firestore (NoSQL)
- **Authentication**: JWT (JSON Web Tokens) + SNS OAuth 2.0
- **Social Login**: Google (Firebase Admin SDK), Kakao API, Naver API
- **Validation**: Pydantic 2.11+ (강화된 필드 검증)
- **Password Hashing**: bcrypt
- **Email Service**: AWS SES / Gmail SMTP
- **External API**: 축산물품질평가원 OpenAPI

### AI & Machine Learning
- **AI Framework**: LangGraph (대화 플로우 관리)
- **LLM**: OpenAI GPT-4o-mini
- **Natural Language**: 한국어 낙농업 전문 대화 시스템
- **Vector Database**: Chroma (RAG 기반 지식 검색)
- **Embedding**: OpenAI Embeddings

### Infrastructure
- **Deployment**: AWS EC2 (Ubuntu)
- **CI/CD**: GitHub Actions
- **Process Management**: tmux
- **Web Server**: uvicorn (ASGI)
- **Environment**: Python venv

### 외부 연동
- **축산물이력제**: 축산물품질평가원 (EKAPE) OpenAPI
- **API 방식**: REST API (XML 응답)
- **조회 정보**: 7가지 옵션 (기본정보, 농장이력, 도축정보, 백신정보 등)

## 🔍 문제 해결

### API 사용 시 주의사항

#### 1. 인증 토큰 관리
- Access Token 만료 시간: 30분
- Refresh Token을 사용하여 갱신 필요
- 로그아웃 시 토큰 삭제 권장

#### 2. 데이터 검증
- **날짜 형식**: YYYY-MM-DD
- **시간 형식**: HH:MM:SS 또는 HH:MM
- **이표번호**: 12자리 숫자 (002로 시작)
- **착유량**: 0보다 큰 값 (리터 단위)

#### 3. 축산물이력제 연동
- **API 키 설정**: `LIVESTOCK_TRACE_API_DECODING_KEY` 환경변수 필수
- **이표번호 형식**: 정확히 12자리 숫자
- **응답 시간**: 비동기 처리로 성능 최적화
- **오류 처리**: 일부 API 실패해도 나머지 정보 수집 계속
- **캐싱**: 5분간 API 응답 캐시로 불필요한 호출 방지

#### 4. SNS 로그인 설정
- **Google**: Firebase 프로젝트의 Admin SDK 키 파일 (`firebase-adminsdk.json`) 필요
- **Kakao**: 클라이언트측에서 액세스 토큰 획득 후 서버로 전달
- **Naver**: 환경변수 필수 - `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`
- **자동 사용자 생성**: 첫 로그인 시 사용자 및 농장 정보 자동 생성
- **토큰 검증**: 각 플랫폼의 API를 통해 액세스 토큰 유효성 실시간 검증
- **JWT 발급**: SNS 로그인 성공 시 자체 JWT 토큰 자동 발급

#### 5. AI 챗봇 사용
- **OpenAI API 키**: `OPENAI_API_KEY` 환경변수 필수
- **질문 언어**: 한국어 권장 (낙농업 전문용어 특화)
- **응답 시간**: 일반적으로 2-5초 소요
- **질문 분류**: 시스템이 자동으로 적절한 응답 경로 선택
- **이표번호 인식**: 12자리 숫자 패턴을 자동으로 감지하여 농장 데이터 조회
- **메모리 관리**: 채팅방별 대화 맥락 유지, 14일 후 자동 정리

#### 6. 에러 처리
```typescript
// 표준 에러 응답 형태
interface ApiError {
  detail: string;
  status_code: number;
}

// SNS 로그인 에러 처리 예시
interface SNSLoginError {
  detail: string;
  status_code: number;
  provider: string; // "google" | "kakao" | "naver"
}

try {
  const response = await fetch('/sns/google/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      access_token: 'google_access_token_here'
    })
  });
  
  if (!response.ok) {
    const error: SNSLoginError = await response.json();
    console.error('SNS Login Error:', error.detail);
    // 토큰 만료나 유효하지 않은 토큰 처리
  }
  
  const result = await response.json();
  console.log('로그인 성공:', result.access_token);
} catch (error) {
  console.error('Network Error:', error);
}

// AI 챗봇 에러 처리 예시
try {
  const response = await fetch('/chatbot/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: 'user123',
      chat_id: 'chat-uuid-123', 
      question: '젖소 발정 증상이 뭔가요?'
    })
  });
  
  if (!response.ok) {
    const error: ApiError = await response.json();
    console.error('Chatbot API Error:', error.detail);
  }
  
  const result = await response.json();
  console.log('AI 응답:', result.answer);
} catch (error) {
  console.error('Network Error:', error);
}
```

## 🚀 배포

### GitHub Actions 자동 배포
1. **트리거**: `main` 브랜치 푸시 시 자동 실행
2. **배포 과정**:
   - 코드 업데이트 (`git pull origin main`)
   - 의존성 설치 (`pip install -r requirements.txt`)
   - 환경변수 자동 설정
   - 서버 재시작 (tmux session)
   - 헬스체크 확인

## 📞 지원 및 연락처

### 기술 지원
- **GitHub**: [BlackCows-Team/blackcows-server](https://github.com/BlackCows-Team/blackcows-server)
- **Issues**: [GitHub Issues](https://github.com/BlackCows-Team/blackcows-server/issues)
- **이메일**: team@blackcowsdairy.com

## 🔄 API 사용 패턴

### 1. 젖소 등록 워크플로우
```
사용자 입력: 이표번호
     ↓
등록 상태 확인 API
     ↓
┌─ 이미 등록됨 → 오류 메시지
├─ 축산물이력제 정보 있음 → 자동 등록
└─ 정보 없음 → 수동 등록
     ↓
등록 완료 → 젖소 목록 조회
```

### 2. 기록 관리 워크플로우
```
기록 유형 선택 (착유/발정/치료 등)
     ↓
젖소 선택
     ↓
기록 데이터 입력
     ↓
기록 생성 API 호출
     ↓
성공 → 기록 목록 업데이트
```

### 3. AI 챗봇 사용 패턴
```
사용자 질문 입력
     ↓
LangGraph 질문 분류 시스템
     ↓
┌─ 낙농 지식 → RAG 검색 → 전문 답변
├─ 농장 데이터 → 젖소 정보 조회 → 맞춤 답변  
├─ 일반 대화 → 메모리 기반 → 자연스러운 응답
└─ 무관한 질문 → 안내 메시지
     ↓
응답 생성 + 대화 이력 저장
     ↓
연속 대화 지원 (메모리 유지)
```

### 4. AI 챗봇 고급 활용
```javascript
// 농장 데이터 연동 질문 예시
const farmDataQuestions = [
  "002123456789번 소 최근 착유량 어떻게 돼?",
  "어제 분만한 소들 있어?", 
  "건강 검진이 필요한 소 알려줘",
  "발정기인 소들 현황 보여줘"
];

// 낙농 지식 질문 예시  
const knowledgeQuestions = [
  "젖소 발정 주기는 얼마나 돼?",
  "착유기 청소는 어떻게 해야 해?",
  "송아지 이유식은 언제부터 줘야 해?",
  "유방염 증상이 뭐야?"
];

// 연속 대화 예시
async function chatWithSodam() {
  // 1. 첫 번째 질문
  await askChatbot("젖소 발정 증상이 뭐야?");
  
  // 2. 후속 질문 (이전 맥락 유지)
  await askChatbot("그럼 발정 확인은 어떻게 해?");
  
  // 3. 농장 데이터와 연결
  await askChatbot("우리 농장에서 발정기인 소 있어?");
}
```

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.



### 🤖 AI 챗봇 API (`/chatbot`) - ⭐ 핵심 기능

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/chatbot/ask` | **챗봇 질문하기** | `user_id`, `chat_id`, `question` | `answer` |
| `GET` | `/chatbot/rooms/{user_id}` | **사용자 채팅방 목록 조회** | `user_id` (경로) | `chats: [{chat_id, created_at}]` |
| `POST` | `/chatbot/rooms` | **새로운 채팅방 생성** | `user_id`, `name` | `chats: [{chat_id, created_at}]` |
| `PUT` | `/chatbot/rooms/{chat_id}/name` | **채팅방 이름 변경** | `chat_id`, `name` | 변경 확인 메시지 |
| `GET` | `/chatbot/history/{chat_id}` | **채팅방 대화 이력 조회** | `chat_id` (경로) | `chat_id`, `messages: [{role, content, timestamp}]` |
| `DELETE` | `/chatbot/rooms/{chat_id}` | **채팅방 및 메시지 삭제** | `chat_id` (경로) | `detail: 삭제 결과 메시지` |
| `DELETE` | `/chatbot/rooms/expired/auto` | **14일 이상된 채팅방 자동 삭제** | 없음 | `detail: 삭제 결과 메시지` |

#### 🤖 AI 챗봇 "소담이" 상세 기능

**소담이의 특징:**
- **이름**: 소담이 (낙농업 전문 AI 어시스턴트)
- **AI 엔진**: OpenAI GPT-4o-mini
- **프레임워크**: LangGraph 기반 고급 대화 플로우 관리
- **언어 지원**: 한국어 전용 (낙농업 전문용어 특화)

**질문 자동 분류 시스템:**

소담이는 사용자의 질문을 다음 4가지로 자동 분류하여 최적의 응답을 제공합니다:

1. **rag (낙농 지식 질문)**
   - 낙농업 관련 전문 정보, 기술, 정책, 용어 등
   - 예시: "젖소의 발정 주기는?", "착유기는 어떻게 작동하나요?", "낙농업 역사 알려줘"

2. **cow_info (농장 데이터 질문)**
   - 사용자의 농장에 등록된 소 정보나 상태, 기록 등
   - 예시: "103번 소 상태 알려줘", "어제 분만한 소들 누구야?", "이표번호 002123456789 소 정보"

3. **general (일반 대화)**
   - 챗봇 자체에 대한 질문, 인사, 감정 표현, 잡담 등
   - 예시: "안녕", "이전 질문 뭐였지?", "소담이 귀엽다", "고마워", "너 누구야?"

4. **irrelevant (무관한 질문)**
   - 낙농업 또는 사용자의 목장과 완전히 무관한 질문
   - 예시: "로또 번호 알려줘", "요즘 주식 어때요?", "오늘 점심 뭐 먹지?"

**AI 챗봇 사용 방법:**

```javascript
// 1. 새 채팅방 생성
POST /chatbot/rooms
{
  "user_id": "user123",
  "name": "새로운 대화"  // 선택적
}

// 2. 질문하기
POST /chatbot/ask
{
  "user_id": "user123",
  "chat_id": "chat-uuid-123",
  "question": "젖소 발정 증상이 뭔가요?"
}

// 3. 대화 이력 조회
GET /chatbot/history/chat-uuid-123

// 4. 사용자의 모든 채팅방 조회
GET /chatbot/rooms/user123

// 5. 채팅방 이름 변경
PUT /chatbot/rooms/chat-uuid-123/name
{
  "name": "발정 관련 상담"
}
```

**AI 챗봇 응답 예시:**

- **낙농 지식 질문**: "젖소의 발정 주기는 평균 21일입니다. 발정 증상으로는 다른 소에게 올라타거나, 불안해하며 울음소리를 내는 행동을 보입니다..."

- **농장 데이터 질문**: "꽃분이(002123456789) 소의 최근 착유 기록: 착유량 25.5L, 1회차, 유지방 3.8% (날짜: 2025-06-27)"

- **일반 대화**: "안녕하세요! 저는 낙농업 도우미 소담이예요. 젖소 관리나 낙농업에 관한 궁금한 점이 있으시면 언제든 물어보세요!"



## 🚀 최근 업데이트 (v2.8.0)

### ✅ 2025년 7월 4일 - 할일 관리 시스템 개선 및 라우터 구조 최적화

#### 🔧 주요 수정사항
- **라우터 prefix 중복 문제 해결**: 307 Temporary Redirect 및 라우팅 오류 완전 해결
- **Firestore 쿼리 최적화**: 복잡한 복합 쿼리 문제 해결로 500 Internal Server Error 수정
- **API 경로 개선**: 라우터 충돌 해결로 정상적인 API 호출 가능
- **클라이언트 사이드 필터링**: 성능 향상을 위한 쿼리 단순화
- **인증 테스트 엔드포인트 추가**: 디버깅을 위한 `/api/todos/test-auth` 추가

#### 🚨 라우터 구조 수정 (중요!)
**문제**: 라우터 prefix 중복으로 인한 `/api/todos/api/todos` 경로 생성
**해결**: 
- `routers/task.py`에서 `prefix="/api/todos"` 제거
- `main.py`에서 `prefix="/api/todos"` 명시적 추가
- 결과: 정상적인 `/api/todos/...` 경로로 API 호출 가능

#### 📋 할일 관리 API 경로 (수정 완료)
| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/api/todos/test-auth` | **인증 테스트** (디버깅용) |
| `POST` | `/api/todos/create` | **할일 생성** |
| `GET` | `/api/todos/` | **할일 목록 조회** |
| `GET` | `/api/todos/today` | **오늘 할일 조회** |
| `GET` | `/api/todos/overdue` | **지연된 할일 조회** |
| `GET` | `/api/todos/statistics` | **할일 통계 조회** |
| `GET` | `/api/todos/calendar` | **캘린더 뷰 조회** |
| `GET` | `/api/todos/{task_id}` | **할일 상세 조회** |
| `PUT` | `/api/todos/{task_id}/update` | **할일 수정** |
| `PATCH` | `/api/todos/{task_id}/complete` | **할일 완료 처리** |
| `DELETE` | `/api/todos/{task_id}` | **할일 삭제** |

#### 🐛 해결된 문제들
- **307 Temporary Redirect 해결**: 라우터 prefix 중복 문제 완전 해결
- **500 Internal Server Error 해결**: Firestore 복합 쿼리 인덱스 문제 해결
- **401 Unauthorized 해결**: 인증 토큰 검증 문제 해결
- **할일 목록 조회 성능 개선**: 클라이언트 사이드 필터링으로 쿼리 최적화
- **Flutter 앱 네트워크 오류 해결**: 예상 경로와 실제 경로 일치로 정상 동작

#### 🔄 Flutter 앱 수정 완료사항
```dart
// 할일 생성 - 정상 경로
final response = await http.post(
  Uri.parse('$baseUrl/api/todos/create'),
  headers: {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json',
  },
  body: json.encode(taskData),
);

// 할일 수정 - 정상 경로
final response = await http.put(
  Uri.parse('$baseUrl/api/todos/$taskId/update'),
  headers: {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json',
  },
  body: json.encode(updateData),
);

// 할일 목록 조회 - 정상 경로
final response = await http.get(
  Uri.parse('$baseUrl/api/todos/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
  },
);
```

#### ✅ 수정 완료 확인
- **라우터 구조**: `routers/task.py`에서 prefix 제거, `main.py`에서 명시적 추가
- **API 경로**: 모든 할일 관리 API가 `/api/todos/...`로 정상 동작
- **클라이언트 호환성**: Flutter 앱에서 기존 경로 그대로 사용 가능
- **오류 해결**: 307, 500, 401 오류 모두 해결됨

### ✅ 2025년 1월 26일 - 할일 관리 시스템 출시

#### 🆕 새로운 기능
- **할일 관리 시스템**: 개인/젖소별/농장 전체 할일 관리
- **우선순위 시스템**: 낮음/보통/높음/긴급 4단계 우선순위
- **카테고리 분류**: 착유, 치료, 백신, 검진, 번식, 사료, 시설관리 등
- **반복 일정**: 매일/주/월/년 반복 할일 설정
- **자동 지연 감지**: 마감일 지난 할일 자동 상태 변경
- **통계 및 분석**: 완료율, 카테고리별 분포, 우선순위별 분석
- **캘린더 뷰**: 날짜별 할일 그룹화 및 시각화

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.

---

**개발팀**: BlackCows Team  
**버전**: v2.8.0  
**최종 업데이트**: 2025년 1월 27일  
**주요 변경사항**: 라우터 prefix 중복 문제 해결, 할일 관리 시스템 최적화, 307/500/401 오류 완전 해결
