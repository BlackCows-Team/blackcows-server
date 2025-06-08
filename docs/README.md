# 🐄 낙농 관리 시스템 API

> **Flutter 앱과 연동되는 종합적인 젖소 관리 및 기록 시스템**

## 📋 프로젝트 개요

낙농업체를 위한 종합 관리 시스템으로, 젖소 정보 관리와 다양한 기록 관리를 지원하는 RESTful API입니다.

### 🎯 주요 기능

#### 🐮 젖소 관리
- ✅ 젖소 등록/수정/삭제 (이표번호, 센서번호 관리)
- ✅ 즐겨찾기 기능 (홈화면 노출용)
- ✅ 상세 정보 조회 및 검색
- ✅ 농장별 통계 제공

#### 📝 기록 관리
- ✅ **번식기록**: 인공수정, 임신확인, 분만예정일 등
- ✅ **질병기록**: 증상, 치료내용, 약물, 비용 등
- ✅ **분류변경**: 상태변경 사유 및 담당자 기록
- ✅ **기타기록**: 체중측정, 백신접종 등 자유 기록

#### 🔐 보안 및 인증
- ✅ JWT 기반 사용자 인증
- ✅ 농장별 데이터 격리
- ✅ Firebase 기반 보안 규칙

## 🏗️ 시스템 아키텍처

```
Flutter App (Client)
      ↕️
FastAPI Server (Backend)
      ↕️
Firebase Firestore (Database)
```

### 📊 데이터베이스 구조

#### 컬렉션: `cows` (젖소 정보)
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
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

#### 컬렉션: `cow_records` (기록 정보)
```json
{
  "id": "uuid",
  "cow_id": "cow_uuid",
  "record_type": "breeding|disease|status_change|other",
  "record_date": "2025-06-09",
  "title": "기록 제목",
  "description": "상세 설명",
  "record_data": {
    // 기록 유형별 상세 데이터
  },
  "farm_id": "farm_uuid",
  "owner_id": "user_uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

## 🚀 설치 및 실행

### 1️⃣ 환경 설정

```bash
# 레포지토리 클론
git clone <repository_url>
cd dairy-management-api

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 Firebase 설정 및 JWT 키 입력
```

### 2️⃣ Firebase 설정

1. Firebase Console에서 프로젝트 생성
2. Firestore Database 활성화
3. 서비스 계정 키 다운로드
4. `.env` 파일에 Firebase 설정 추가

### 3️⃣ 서버 실행

```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4️⃣ API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API 엔드포인트

### 🐮 젖소 관리 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/cows/` | 젖소 등록 |
| `GET` | `/cows/` | 젖소 목록 조회 |
| `GET` | `/cows/{cow_id}` | 젖소 상세 조회 |
| `PUT` | `/cows/{cow_id}` | 젖소 정보 수정 |
| `DELETE` | `/cows/{cow_id}` | 젖소 삭제 |
| `POST` | `/cows/{cow_id}/favorite` | 즐겨찾기 토글 |
| `GET` | `/cows/favorites/list` | 즐겨찾기 목록 |
| `GET` | `/cows/search/by-tag/{ear_tag_number}` | 이표번호 검색 |
| `GET` | `/cows/statistics/summary` | 농장 통계 |

### 📝 기록 관리 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/records/breeding` | 번식기록 생성 |
| `POST` | `/records/disease` | 질병기록 생성 |
| `POST` | `/records/status-change` | 분류변경 기록 생성 |
| `POST` | `/records/other` | 기타기록 생성 |
| `GET` | `/records/cow/{cow_id}` | 젖소별 기록 조회 |
| `GET` | `/records/` | 농장 전체 기록 조회 |
| `GET` | `/records/{record_id}` | 기록 상세 조회 |
| `PUT` | `/records/{record_id}` | 기록 수정 |
| `DELETE` | `/records/{record_id}` | 기록 삭제 |
| `GET` | `/records/recent/summary` | 최근 기록 조회 |
| `GET` | `/records/statistics/summary` | 기록 통계 |

### 🔐 인증 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/auth/register` | 회원가입 |
| `POST` | `/auth/login` | 로그인 |
| `GET` | `/auth/me` | 내 정보 조회 |

## 💻 Flutter 앱 연동 예시

### 젖소 등록
```dart
Future<void> registerCow() async {
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
    }),
  );
}
```

### 즐겨찾기 토글
```dart
Future<void> toggleFavorite(String cowId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/cows/$cowId/favorite'),
    headers: {'Authorization': 'Bearer $accessToken'},
  );
}
```

### 기록 작성
```dart
Future<void> createBreedingRecord(String cowId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/records/breeding'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      'cow_id': cowId,
      'record_date': '2025-06-09',
      'title': '인공수정 실시',
      'breeding_method': 'artificial',
      'breeding_date': '2025-06-09',
    }),
  );
}
```

## 🧪 테스트

### API 테스트 실행
```bash
# 테스트 스크립트 실행
python api_test_examples.py
```

### Postman 테스트
1. `api_test_examples.py` 파일의 Postman 컬렉션 가이드 참조
2. 환경변수 설정: `base_url`, `access_token`
3. 순차적으로 API 테스트 진행

## 🔧 데이터베이스 최적화

### 필수 인덱스 설정
Firebase Console에서 다음 복합 인덱스들을 설정해야 합니다:

1. **젖소 목록 조회용**
   - `farm_id` (오름차순) + `is_active` (오름차순) + `created_at` (내림차순)

2. **즐겨찾기 조회용**
   - `farm_id` (오름차순) + `is_favorite` (오름차순) + `is_active` (오름차순)

3. **기록 조회용**
   - `cow_id` (오름차순) + `farm_id` (오름차순) + `is_active` (오름차순) + `record_date` (내림차순)

자세한 최적화 가이드는 `database_optimization.md` 파일을 참조하세요.

## 📱 Flutter 앱 화면 구성

### 1. 홈 화면
- ✅ 즐겨찾기된 젖소 목록 표시
- ✅ 최근 기록 요약 표시
- ✅ 농장 통계 대시보드

### 2. 소 관리 탭
- ✅ 전체 젖소 목록
- ✅ 즐겨찾기 별 아이콘
- ✅ 검색 및 필터링
- ✅ 젖소 상세 정보 화면

### 3. 기록 작성 화면
- ✅ 4가지 기록 유형별 입력 폼
- ✅ 날짜 선택기
- ✅ 사진 첨부 (계획)
- ✅ 유효성 검사
