# 🐄 BlackCows 젖소 관리 시스템

> **Flutter 앱과 연동되는 종합적인 젖소 관리 및 기록 시스템 API**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
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

## 🏗️ 시스템 아키텍처

```
Flutter App (Client)
      ↕️ HTTPS/REST API
FastAPI Server (Backend)
      ↕️ Firebase Admin SDK
Firebase Firestore (Database)
      ↕️ CI/CD Pipeline
AWS EC2 (Production Server)
      ↕️ GitHub Actions
Deployment Automation
```

### 📊 데이터베이스 구조

#### 🐮 젖소 정보 컬렉션: `cows`
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

#### 📝 상세 기록 컬렉션: `cow_detailed_records`
```json
{
  "id": "uuid",
  "cow_id": "cow_uuid",
  "record_type": "milking",
  "record_date": "2025-06-16",
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

#### 👥 사용자 정보 컬렉션: `users`
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

## 🚀 설치 및 실행

### 📋 시스템 요구사항

- **Python**: 3.11 이상
- **Node.js**: 16 이상 (Firebase CLI용)
- **Firebase 프로젝트**: Firestore 활성화 필요
- **메모리**: 최소 2GB RAM
- **저장공간**: 최소 1GB

### 1️⃣ 환경 설정

```bash
# 레포지토리 클론
git clone https://github.com/SeulGi0117/blackcows-server.git
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
# JWT 설정
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 환경 설정
ENVIRONMENT=development

# Firebase 설정 (방법 1: JSON 파일 경로)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json

# Firebase 설정 (방법 2: 개별 환경변수)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"

# 이메일 설정 (AWS SES 또는 Gmail)
MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
MAIL_FROM=noreply@yourfarm.com
MAIL_SERVER=email-smtp.ap-northeast-2.amazonaws.com
MAIL_PORT=587
MAIL_TLS=True
MAIL_SSL=False
```

### 3️⃣ Firebase 설정

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. Firestore Database 활성화 (위치: `asia-northeast3` 권장)
3. 서비스 계정 키 생성:
   ```bash
   # Firebase CLI 설치
   npm install -g firebase-tools
   
   # Firebase 로그인
   firebase login
   
   # 프로젝트 초기화
   firebase init firestore
   ```
4. 보안 규칙 설정 (30일 임시 규칙이 적용되어 있음)

### 4️⃣ 서버 실행

```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5️⃣ API 문서 확인

서버 실행 후 브라우저에서 접속:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health
- **Server Info**: http://localhost:8000/

## 📡 API 엔드포인트

### 🔐 인증 API
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| `POST` | `/auth/register` | 회원가입 (목장별명 포함) | ✅ |
| `POST` | `/auth/login` | 로그인 (user_id 기반) | ✅ |
| `POST` | `/auth/refresh` | 토큰 갱신 | ✅ |
| `GET` | `/auth/me` | 내 정보 조회 | ✅ |
| `POST` | `/auth/find-user-id` | 아이디 찾기 | ✅ |
| `POST` | `/auth/request-password-reset` | 비밀번호 재설정 요청 | ✅ |
| `POST` | `/auth/reset-password` | 비밀번호 재설정 | ✅ |
| `DELETE` | `/auth/delete-account` | 회원탈퇴 | ✅ |

### 🐮 젖소 관리 API
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| `POST` | `/cows/` | 젖소 등록 | ✅ |
| `GET` | `/cows/` | 젖소 목록 조회 | ✅ |
| `GET` | `/cows/{cow_id}` | 젖소 상세 조회 | ✅ |
| `PUT` | `/cows/{cow_id}` | 젖소 정보 수정 | ✅ |
| `DELETE` | `/cows/{cow_id}` | 젖소 삭제 | ✅ |
| `POST` | `/cows/{cow_id}/favorite` | 즐겨찾기 토글 | ✅ |
| `GET` | `/cows/favorites/list` | 즐겨찾기 목록 | ✅ |
| `GET` | `/cows/search/by-tag/{ear_tag_number}` | 이표번호 검색 | ✅ |
| `GET` | `/cows/statistics/summary` | 농장 통계 | ✅ |

### 🐮 젖소 상세정보 API
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| `PUT` | `/cows/{cow_id}/details` | 상세정보 업데이트 | ✅ |
| `GET` | `/cows/{cow_id}/details` | 상세정보 조회 | ✅ |
| `GET` | `/cows/{cow_id}/has-details` | 상세정보 보유 여부 | ✅ |

### 📝 상세 기록 관리 API

#### 🥛 착유 기록 API (핵심 기능)
| Method | Endpoint | 설명 | 필수 필드 |
|--------|----------|------|----------|
| `POST` | `/detailed-records/milking` | 착유 기록 생성 | `record_date`, `milk_yield` |
| `GET` | `/detailed-records/cow/{cow_id}/milking` | 젖소별 착유 기록 조회 | - |
| `GET` | `/detailed-records/milking/recent` | 최근 착유 기록 조회 | - |

#### 기타 상세 기록 API
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| `POST` | `/detailed-records/estrus` | 발정 기록 생성 | ✅ |
| `POST` | `/detailed-records/insemination` | 인공수정 기록 생성 | ✅ |
| `POST` | `/detailed-records/pregnancy-check` | 임신감정 기록 생성 | ✅ |
| `POST` | `/detailed-records/calving` | 분만 기록 생성 | ✅ |
| `POST` | `/detailed-records/feed` | 사료급여 기록 생성 | ✅ |
| `POST` | `/detailed-records/health-check` | 건강검진 기록 생성 | ✅ |
| `POST` | `/detailed-records/vaccination` | 백신접종 기록 생성 | ✅ |
| `POST` | `/detailed-records/weight` | 체중측정 기록 생성 | ✅ |
| `POST` | `/detailed-records/treatment` | 치료 기록 생성 | ✅ |
| `GET` | `/detailed-records/cow/{cow_id}` | 젖소별 기록 조회 | ✅ |
| `GET` | `/detailed-records/{record_id}` | 기록 상세 조회 | ✅ |
| `DELETE` | `/detailed-records/{record_id}` | 기록 삭제 | ✅ |

### 📊 통계 및 분석 API
| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| `GET` | `/detailed-records/cow/{cow_id}/milking/statistics` | 착유 통계 | ✅ |
| `GET` | `/detailed-records/cow/{cow_id}/weight/trend` | 체중 변화 추이 | ✅ |
| `GET` | `/detailed-records/cow/{cow_id}/reproduction/timeline` | 번식 타임라인 | ✅ |
| `GET` | `/detailed-records/cow/{cow_id}/summary` | 젖소 기록 요약 | ✅ |

## 💻 Flutter 앱 연동 예시

### 회원가입 및 로그인
```dart
// 회원가입
Future<Map<String, dynamic>> registerUser() async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/register'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      'username': '홍길동',
      'user_id': 'admin123',
      'email': 'admin@farm.com',
      'password': 'password123',
      'password_confirm': 'password123',
      'farm_nickname': '행복농장',
    }),
  );
  return json.decode(response.body);
}

// 로그인
Future<Map<String, dynamic>> loginUser() async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/login'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      'user_id': 'admin123',
      'password': 'password123',
    }),
  );
  return json.decode(response.body);
}
```

### 젖소 등록
```dart
Future<Map<String, dynamic>> registerCow() async {
  final response = await http.post(
    Uri.parse('$baseUrl/cows/'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      'ear_tag_number': '002123456789',
      'name': '꽃분이',
      'birthdate': '2022-03-15',
      'sensor_number': '1234567890123',
      'health_status': 'good',
      'breeding_status': 'lactating',
      'breed': 'Holstein',
    }),
  );
  return json.decode(response.body);
}
```

### 🥛 착유 기록 생성 (핵심 기능)
```dart
// 필수 필드만으로 착유 기록 생성
Future<Map<String, dynamic>> createBasicMilkingRecord(String cowId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/detailed-records/milking'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      // 필수 필드
      'cow_id': cowId,
      'record_date': '2025-06-19',  // 필수: 착유 날짜
      'milk_yield': 25.5,           // 필수: 착유량 (리터)
    }),
  );
  return json.decode(response.body);
}

// 상세 정보 포함 착유 기록 생성
Future<Map<String, dynamic>> createDetailedMilkingRecord(String cowId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/detailed-records/milking'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      // 필수 필드
      'cow_id': cowId,
      'record_date': '2025-06-19',
      'milk_yield': 25.5,
      
      // 선택적 필드
      'milking_start_time': '06:00:00',
      'milking_end_time': '06:20:00',
      'milking_session': 1,
      'fat_percentage': 3.8,
      'protein_percentage': 3.2,
      'somatic_cell_count': 150000,
      'temperature': 37.5,
      'conductivity': 5.2,
      'blood_flow_detected': false,
      'color_value': '정상',
      'air_flow_value': 2.1,
      'lactation_number': 3,
      'rumination_time': 480,
      'collection_code': 'AUTO',
      'collection_count': 1,
      'notes': '정상 착유, 컨디션 양호',
    }),
  );
  return json.decode(response.body);
}
```

### 상세정보 업데이트
```dart
Future<Map<String, dynamic>> updateCowDetails(String cowId) async {
  final response = await http.put(
    Uri.parse('$baseUrl/cows/$cowId/details'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      'body_weight': 450.5,
      'lactation_number': 3,
      'temperament': 'gentle',
      'barn_section': 'A동',
      'stall_number': 'A-15',
      'purchase_price': 2500000,
    }),
  );
  return json.decode(response.body);
}
```

## 🧪 테스트

### API 테스트 예시

```bash
# 회원가입 테스트
curl -X POST "http://localhost:8000/auth/register" \
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
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin123",
    "password": "password123"
  }'

# 착유 기록 생성 테스트 (필수 필드만)
curl -X POST "http://localhost:8000/detailed-records/milking" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -d '{
    "cow_id": "your-cow-id",
    "record_date": "2025-06-19",
    "milk_yield": 25.5
  }'

# 착유 기록 생성 테스트 (상세 정보 포함)
curl -X POST "http://localhost:8000/detailed-records/milking" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -d '{
    "cow_id": "your-cow-id",
    "record_date": "2025-06-19",
    "milk_yield": 25.5,
    "milking_start_time": "06:00:00",
    "fat_percentage": 3.8,
    "protein_percentage": 3.2,
    "somatic_cell_count": 150000
  }'
```

### Postman 테스트 컬렉션

1. **환경변수 설정**:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (로그인에서 받은 토큰)

2. **테스트 순서**:
   ```
   POST /auth/register → 회원가입
   POST /auth/login → access_token 저장
   POST /cows/ → cow_id 저장
   PUT /cows/{{cow_id}}/details → 상세정보 입력
   POST /detailed-records/milking → 착유 기록 생성
   GET /detailed-records/cow/{{cow_id}}/milking → 착유 기록 조회
   ```

## 🚀 배포

### AWS EC2 자동 배포

GitHub Actions를 통한 자동 배포가 설정되어 있습니다:

1. **트리거**: `main` 브랜치에 푸시 시 자동 실행
2. **배포 과정**:
   - ✅ 코드 업데이트 (`git pull origin main`)
   - ✅ 의존성 설치 (`pip install -r requirements.txt`)
   - ✅ 환경변수 자동 설정
   - ✅ Firebase 서비스 계정 키 검증
   - ✅ Python 구문 검사
   - ✅ 서버 재시작 (tmux session 0)
   - ✅ 헬스체크 확인
   - ✅ 포트 상태 확인

3. **배포 상태 확인**:
   - 서버 접속: http://52.78.212.96:8000
   - API 문서: http://52.78.212.96:8000/docs
   - 헬스체크: http://52.78.212.96:8000/health

### 수동 배포

```bash
# EC2 서버 접속
ssh -i your-key.pem ubuntu@52.78.212.96

# 코드 업데이트
cd ~/blackcows-server
git pull origin main

# tmux 세션 접속 (서버 로그 확인)
tmux attach-session -t 0

# tmux 세션 나가기: Ctrl+B → D
```

## 🔧 데이터베이스 최적화

### 필수 Firestore 인덱스

Firebase Console에서 다음 복합 인덱스들을 설정해야 합니다:

1. **젖소 목록 조회용**:
   - `farm_id` (오름차순) + `is_active` (오름차순) + `created_at` (내림차순)

2. **즐겨찾기 조회용**:
   - `farm_id` (오름차순) + `is_favorite` (오름차순) + `is_active` (오름차순)

3. **상세 기록 조회용** (착유 기록 포함):
   - `cow_id` (오름차순) + `farm_id` (오름차순) + `record_type` (오름차순) + `record_date` (내림차순)

4. **착유 기록 전용 인덱스**:
   - `farm_id` (오름차순) + `record_type` (오름차순) + `record_date` (내림차순) + `created_at` (내림차순)

5. **사용자 인증용**:
   - `user_id` (오름차순) + `is_active` (오름차순)
   - `email` (오름차순) + `is_active` (오름차순)

### 인덱스 자동 배포
```bash
# Firebase CLI로 인덱스 배포
firebase deploy --only firestore:indexes
```

## 📱 Flutter 앱 화면 구성

### 1. 홈 화면
- ✅ 즐겨찾기된 젖소 목록 표시
- ✅ 최근 기록 요약 표시
- ✅ 농장 통계 대시보드
- ✅ 빠른 착유 기록 버튼

### 2. 소 관리 탭
- ✅ 전체 젖소 목록
- ✅ 즐겨찾기 별 아이콘
- ✅ 검색 및 필터링
- ✅ 젖소 상세 정보 화면

### 3. 기록 관리 탭
- ✅ 10가지 상세 기록 유형별 입력 폼
- ✅ 날짜 선택기 및 유효성 검사
- ✅ 기록 목록 및 통계 화면
- 🆕 **착유 기록 입력 폼** (필수 필드: 착유 날짜, 착유량)

### 4. 착유 기록 상세 페이지
- ✅ 기본 정보 (젖소명, 이표번호)
- ✅ 착유 정보 (착유량, 시간, 횟수)
- ✅ 품질 정보 (유지방, 유단백, 체세포수)
- ✅ 센서 데이터 (온도, 전도율, 공기흐름 등)
- ✅ 과거 기록 조회 및 통계

### 5. 인증 화면
- ✅ 회원가입 (목장별명 입력)
- ✅ 로그인 (아이디 기반)
- ✅ 아이디/비밀번호 찾기
- ✅ 비밀번호 재설정 (이메일 토큰)

## 🆕 최근 업데이트 (2025-06-19)

### 착유 기록 API 개선사항

#### 1. **필수 필드 강화**
- **착유 날짜** (`record_date`): YYYY-MM-DD 형식, 필수 입력
- **착유량** (`milk_yield`): 리터 단위, 0보다 큰 값, 필수 입력

#### 2. **유효성 검사 강화**
- 날짜 형식 검증 (YYYY-MM-DD)
- 착유량 범위 검증 (0-100L)
- 시간 형식 검증 (HH:MM:SS 또는 HH:MM)
- 비율 필드 검증 (0-10%)

#### 3. **자동 제목/설명 생성**
- 제목: "착유 기록 (25.5L, 1회차, 06:00:00)"
- 설명: "유지방 3.8%, 유단백 3.2%, 체세포수 150,000"

#### 4. **인증 시스템 개선**
- JWT 기반 비밀번호 재설정
- 이메일 토큰 발송 (AWS SES 지원)
- 회원탈퇴 시 모든 데이터 완전 삭제

#### 5. **에러 처리 개선**
- 명확한 에러 메시지
- 필드별 상세 검증 오류 안내
- HTTP 상태 코드 표준화

#### 6. **새로운 엔드포인트 추가**
- `GET /detailed-records/cow/{cow_id}/milking`: 젖소별 착유 기록 조회
- `GET /detailed-records/milking/recent`: 최근 착유 기록 조회

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI 0.115+ (Python 3.11+)
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

### Development Tools
- **API Documentation**: Swagger UI, ReDoc
- **Code Quality**: Python Type Hints
- **Version Control**: Git (GitHub)
- **Testing**: curl, Postman

## 🔍 문제 해결

### 일반적인 문제들

#### 1. Firebase 연결 오류
```bash
# 환경변수 확인
echo $GOOGLE_APPLICATION_CREDENTIALS

# 서비스 계정 키 파일 확인
ls -la config/service-account-key.json

# Firebase 프로젝트 ID 확인
grep FIREBASE_PROJECT_ID .env
```

#### 2. 포트 충돌
```bash
# 포트 8000 사용 프로세스 확인
lsof -i:8000

# 프로세스 종료
kill -9 <PID>
```

#### 3. 의존성 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 삭제 후 재설치
pip install --no-cache-dir -r requirements.txt
```

#### 4. JWT 토큰 오류
```bash
# JWT 시크릿 키 확인
grep JWT_SECRET_KEY .env

# 토큰 만료 시간 확인
grep TOKEN_EXPIRE .env
```

### 로그 확인

#### 개발 환경
```bash
# 실시간 로그 확인
uvicorn main:app --reload --log-level debug
```

#### 프로덕션 환경 (EC2)
```bash
# tmux 세션 접속
tmux attach-session -t 0

# 최근 로그 확인
tmux capture-pane -t 0 -p | tail -50

# 에러 로그만 확인
tmux capture-pane -t 0 -p | grep -i error
```

## 📈 성능 최적화

### 데이터베이스 최적화
- ✅ Firestore 복합 인덱스 활용
- ✅ 쿼리 제한 (`limit()`) 적용
- ✅ 필드 선택적 조회
- ✅ 소프트 삭제로 데이터 무결성 유지

### API 최적화
- ✅ Pydantic 스키마 검증
- ✅ HTTP 상태 코드 표준화
- ✅ CORS 설정으로 Flutter 연동
- ✅ 에러 응답 구조화

### 보안 강화
- ✅ JWT 토큰 기반 인증
- ✅ 비밀번호 bcrypt 해싱
- ✅ 농장별 데이터 격리
- ✅ API 접근 권한 제어
- ✅ 환경변수 보안 관리

## 🧩 확장 가능성

### 추가 개발 예정 기능
- 🔄 **실시간 알림**: WebSocket 기반 실시간 데이터 동기화
- 📊 **고급 분석**: 머신러닝 기반 착유량 예측
- 📱 **모바일 최적화**: 오프라인 동기화 기능
- 🏭 **다중 농장**: 대규모 농장 그룹 관리
- 📈 **BI 대시보드**: 실시간 비즈니스 인텔리전스
- 🤖 **자동화**: IoT 센서 데이터 자동 수집
- 🌍 **다국어**: 국제 농장 지원

### 아키텍처 확장
- **마이크로서비스**: 서비스별 분리 배포
- **로드밸런싱**: 트래픽 분산 처리  
- **캐싱**: Redis 기반 성능 향상
- **모니터링**: 실시간 시스템 모니터링

## 📊 프로젝트 통계

### 코드 통계
- **총 파일 수**: 30개
- **Python 코드**: ~3,000줄
- **API 엔드포인트**: 35개+
- **데이터 모델**: 15개+
- **테스트 커버리지**: 진행 중

### 기능 완성도
- **인증 시스템**: 100% ✅
- **젖소 관리**: 100% ✅  
- **착유 기록**: 100% ✅
- **상세 기록**: 100% ✅
- **통계 분석**: 90% 🔄
- **배포 자동화**: 100% ✅

## 🤝 기여하기

### 개발 환경 설정
```bash
# 1. 레포지토리 포크
# 2. 로컬 클론
git clone https://github.com/your-username/blackcows-server.git
cd blackcows-server

# 3. 브랜치 생성
git checkout -b feature/new-feature

# 4. 개발 및 테스트
# 5. 커밋 및 푸시
git add .
git commit -m "Add: 새로운 기능 추가"
git push origin feature/new-feature

# 6. Pull Request 생성
```

### 코딩 컨벤션
- **Python**: PEP 8 스타일 가이드 준수
- **API**: RESTful 설계 원칙
- **Commit**: Conventional Commits 형식
- **Documentation**: 코드 주석 및 docstring 작성

### 이슈 리포팅
- **버그 리포트**: [GitHub Issues](https://github.com/SeulGi0117/blackcows-server/issues)
- **기능 제안**: Feature Request 템플릿 사용
- **보안 이슈**: 비공개 메시지로 연락

## 📞 지원 및 연락처

### 기술 지원
- **이메일**: team@blackcowsdairy
- **GitHub**: [@SeulGi0117]([https://github.com/SeulGi0117](https://github.com/BlackCows-Team/blackcows-server))
- **이슈 트래커**: [GitHub Issues]([https://github.com/SeulGi0117/blackcows-server/issues](https://github.com/BlackCows-Team/blackcows-server/issues))

### 문서 및 리소스
- **API 문서**: http://52.78.212.96:8000/docs

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](docs/LICENSE) 하에 배포됩니다.

```
MIT License

Copyright (c) 2025 SeulGi

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

*최종 업데이트: 2025년 6월 19일*
