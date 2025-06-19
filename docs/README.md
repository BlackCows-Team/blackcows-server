# 🐄 BlackCows 젖소 관리 시스템 API

> **Flutter 앱과 연동되는 종합적인 젖소 관리 및 기록 시스템 REST API 서버**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.3.1-green.svg)](https://fastapi.tiangolo.com)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 프로젝트 개요

BlackCows는 낙농업체를 위한 종합 관리 시스템으로, 젖소 정보 관리와 다양한 상세 기록 관리를 지원하는 RESTful API 서버입니다.

### 🎯 주요 기능

#### 🐮 젖소 기본 관리
- ✅ **젖소 등록/수정/삭제** - 이표번호, 센서번호, 기본 정보 관리
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

#### 🔐 보안 및 인증
- ✅ **JWT 기반 사용자 인증** - Access/Refresh Token
- ✅ **농장별 데이터 격리** - 멀티테넌트 지원
- ✅ **Firebase 보안 규칙** - 데이터 접근 제어
- ✅ **비밀번호 재설정** - 이메일 기반 토큰 시스템
- ✅ **회원탈퇴** - 모든 관련 데이터 완전 삭제

## 🚀 서버 상태 확인

- **프로덕션 서버**: http://52.78.212.96:8000
- **헬스 체크**: http://52.78.212.96:8000/health
- **서버 정보**: http://52.78.212.96:8000/

## 📡 전체 API 엔드포인트

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
| `DELETE` | `/auth/delete-account` | 회원탈퇴 | `password`, `confirmation` + Bearer Token | 삭제 완료 메시지 |
| `POST` | `/auth/login-debug` | 로그인 디버깅 | 원시 요청 데이터 | 디버그 정보 |

### 🐮 젖소 관리 API (`/cows`)

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/cows/` | 젖소 등록 | `ear_tag_number`, `name` | 등록된 젖소 정보 |
| `GET` | `/cows/` | 젖소 목록 조회 | Bearer Token | 농장 내 모든 젖소 목록 |
| `GET` | `/cows/{cow_id}` | 젖소 상세 조회 | `cow_id` + Bearer Token | 특정 젖소 상세 정보 |
| `PUT` | `/cows/{cow_id}` | 젖소 정보 수정 | `cow_id` + Bearer Token | 수정된 젖소 정보 |
| `DELETE` | `/cows/{cow_id}` | 젖소 삭제 (소프트 삭제) | `cow_id` + Bearer Token | 삭제 확인 메시지 |
| `PATCH` | `/cows/{cow_id}/favorite` | 즐겨찾기 토글 | `cow_id` + Bearer Token | 즐겨찾기 상태 변경 결과 |
| `GET` | `/cows/favorites/list` | 즐겨찾기 젖소 목록 | Bearer Token | 즐겨찾기된 젖소들 |
| `GET` | `/cows/search/by-tag/{ear_tag_number}` | 이표번호로 젖소 검색 | `ear_tag_number` + Bearer Token | 검색된 젖소 정보 |
| `GET` | `/cows/statistics/summary` | 농장 통계 조회 | Bearer Token | 전체/건강상태별/번식상태별 통계 |

### 🔧 젖소 상세정보 API (`/cows/{cow_id}`)

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `PUT` | `/cows/{cow_id}/details` | 젖소 상세정보 업데이트 | `cow_id` + Bearer Token | 업데이트된 상세정보 |
| `GET` | `/cows/{cow_id}/details` | 젖소 상세정보 조회 | `cow_id` + Bearer Token | 전체 상세정보 포함 젖소 데이터 |
| `GET` | `/cows/{cow_id}/has-details` | 상세정보 보유 여부 확인 | `cow_id` + Bearer Token | `has_detailed_info` boolean |

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
| `DELETE` | `/records/{record_id}` | 기록 삭제 | `record_id` + Bearer Token | 삭제 확인 메시지 |

### 📊 통계 및 분석 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `GET` | `/records/cow/{cow_id}/milking/statistics` | 착유 통계 | `cow_id` + Bearer Token | 일별 착유량, 평균값, 유성분 분석 |
| `GET` | `/records/cow/{cow_id}/weight/trend` | 체중 변화 추이 | `cow_id` + Bearer Token | 기간별 체중 증감 데이터 |
| `GET` | `/records/cow/{cow_id}/reproduction/timeline` | 번식 타임라인 | `cow_id` + Bearer Token | 발정, 수정, 임신, 분만 이력 |
| `GET` | `/records/cow/{cow_id}/summary` | 젖소 기록 요약 | `cow_id` + Bearer Token | 젖소별 기록 현황 요약 |

### 🔍 프론트엔드 전용 조회 API

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

## 📚 API 문서 및 개발 도구

### 🔧 로컬 개발환경에서 Swagger UI 사용

로컬 개발 시에는 Swagger UI를 활용하여 API를 쉽게 테스트할 수 있습니다.

```bash
# 개발 환경으로 서버 실행
ENVIRONMENT=development uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는 개발 스크립트 사용
chmod +x dev_server.sh
./dev_server.sh
```

**로컬 개발 시 접속 가능한 문서:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **OpenAPI 다운로드**: http://localhost:8000/openapi-download

## 🧪 API 테스트

> **⚠️ 중요**: AWS EC2 사용량 절약을 위해 Swagger UI가 비활성화되어 있습니다. 아래 curl 명령어나 Postman을 사용하여 API를 테스트하세요.

### curl 테스트 예시

```bash
# 회원가입 테스트
curl -X POST "http://52.78.212.96:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "홍길동",
    "user_id": "admin123", 
    "email": "admin@farm.com",
    "password": "password123",
    "password_confirm": "password123",
    "farm_nickname": "행복농장"
  }'

# 로그인 테스트
curl -X POST "http://52.78.212.96:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin123",
    "password": "password123"
  }'

# 젖소 목록 조회 테스트
curl -X GET "http://52.78.212.96:8000/cows/" \
  -H "Authorization: Bearer your-access-token"

# 착유 기록 생성 테스트 (필수 필드만)
curl -X POST "http://52.78.212.96:8000/records/milking" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -d '{
    "cow_id": "your-cow-id",
    "record_date": "2025-06-20",
    "milk_yield": 25.5
  }'

# 젖소별 착유 기록 조회
curl -X GET "http://52.78.212.96:8000/records/cow/your-cow-id/milking" \
  -H "Authorization: Bearer your-access-token"

# 농장 통계 조회
curl -X GET "http://52.78.212.96:8000/cows/statistics/summary" \
  -H "Authorization: Bearer your-access-token"
```

## 🔧 설치 및 실행

### 환경 요구사항
- **Python**: 3.11 이상
- **Firebase**: Firestore 데이터베이스
- **Node.js**: 16 이상 (Firebase CLI용)

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

`.env` 파일 생성:
```bash
# 개발 환경 설정
ENVIRONMENT=development

# JWT 설정
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Firebase 설정
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# 이메일 설정 (선택사항)
MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
MAIL_FROM=noreply@yourfarm.com
MAIL_SERVER=email-smtp.ap-northeast-2.amazonaws.com
MAIL_PORT=587
MAIL_TLS=True
MAIL_SSL=False
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
  "ear_tag_number": "002123456789",
  "name": "꽃분이",
  "birthdate": "2022-03-15",
  "sensor_number": "1234567890123",
  "health_status": "good",
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
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

### 📝 상세 기록 컬렉션: `cow_detailed_records`
```json
{
  "id": "uuid",
  "cow_id": "cow_uuid",
  "record_type": "milking",
  "record_date": "2025-06-20",
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

## 🔐 인증 및 보안

### JWT 토큰 시스템
- **Access Token**: 30분 만료, API 호출에 사용
- **Refresh Token**: 7일 만료, Access Token 갱신에 사용
- **Password Reset Token**: 1시간 만료, 비밀번호 재설정 전용

### 비밀번호 재설정 플로우
1. 사용자가 이름, 아이디, 이메일 입력
2. 서버에서 사용자 확인 후 JWT 토큰 생성
3. 이메일로 재설정 링크 발송
4. 사용자가 임시 토큰으로 로그인
5. 새 비밀번호로 변경

### 데이터 보안
- 농장별 데이터 완전 격리
- 소프트 삭제로 데이터 무결성 유지
- bcrypt 비밀번호 해싱
- Firebase Security Rules 적용

## 📈 주요 업데이트 내역


### 새로운 엔드포인트
- `/auth/login-with-reset-token`: 임시 토큰 로그인
- `/auth/change-password`: 비밀번호 변경
- `/auth/delete-account`: 회원탈퇴
- `/records/milking/recent`: 최근 착유 기록 조회
- `/records/cow/{cow_id}/milking/statistics`: 착유 통계 분석

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI 2.3.1 (Python 3.11+)
- **Database**: Firebase Firestore (NoSQL)
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic 2.11+ (강화된 필드 검증)
- **Password Hashing**: bcrypt
- **Email Service**: AWS SES / Gmail SMTP

### Infrastructure
- **Deployment**: AWS EC2 (Ubuntu)
- **CI/CD**: GitHub Actions
- **Process Management**: tmux
- **Web Server**: uvicorn (ASGI)
- **Environment**: Python venv

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

#### 3. 에러 처리
```typescript
// 표준 에러 응답 형태
interface ApiError {
  detail: string;
  status_code: number;
}

// 에러 처리 예시
try {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    const error: ApiError = await response.json();
    console.error('API Error:', error.detail);
  }
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

### 수동 배포
```bash
# EC2 서버 접속
ssh -i your-key.pem ubuntu@52.78.212.96

# 코드 업데이트
cd ~/blackcows-server
git pull origin main

# 서버 재시작
tmux attach-session -t 0
```

## 📞 지원 및 연락처

### 기술 지원
- **GitHub**: [BlackCows-Team/blackcows-server](https://github.com/BlackCows-Team/blackcows-server)
- **Issues**: [GitHub Issues](https://github.com/BlackCows-Team/blackcows-server/issues)
- **이메일**: team@blackcows.com

## 📋 개발 체크리스트

### 백엔드 개발 시
- [ ] 새로운 엔드포인트 추가 후 테스트
- [ ] OpenAPI 문서 업데이트 (`./extract_docs.sh`)
- [ ] 인증이 필요한 API에 `get_current_user` 의존성 추가
- [ ] 데이터 검증 및 에러 처리 구현
- [ ] 농장별 데이터 격리 확인

### 프론트엔드 연동 시
- [ ] 최신 OpenAPI JSON 파일 확인
- [ ] 인증 플로우 구현 (로그인 → 토큰 저장 → API 호출)
- [ ] 토큰 만료 처리 구현
- [ ] 에러 응답 처리 구현
- [ ] 필수 필드 검증 구현

## 📊 프로젝트 통계

- **총 API 엔드포인트**: 60개+
- **지원 기록 유형**: 10가지 (착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료)
- **인증 방식**: JWT (Access/Refresh Token)
- **데이터베이스**: Firebase Firestore (NoSQL)
- **배포 환경**: AWS EC2

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.

```
MIT License

Copyright (c) 2025 BlackCows Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---
최종 업데이트: 2025년 6월 20일

**Q3**: 성능 최적화나 모니터링을 위해 추가로 구현하고 싶은 기능이 있으신가요?

*최종 업데이트: 2025년 6월 20일*
