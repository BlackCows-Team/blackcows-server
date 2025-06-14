# 🐄 BlackCows 젖소 관리 시스템

> **Flutter 앱과 연동되는 종합적인 젖소 관리 및 기록 시스템 API**

## 📋 프로젝트 개요

BlackCows는 낙농업체를 위한 종합 관리 시스템으로, 젖소 정보 관리와 다양한 상세 기록 관리를 지원하는 RESTful API 서버입니다.

### 🎯 주요 기능

#### 🐮 젖소 기본 관리
- ✅ **젖소 등록/수정/삭제** - 이표번호, 센서번호, 기본 정보 관리
- ✅ **즐겨찾기 시스템** - 홈화면 노출용 젖소 선별
- ✅ **상세 정보 관리** - 체중, 산차, 성격, 위치 등 확장 정보
- ✅ **검색 및 통계** - 이표번호 검색, 농장별 통계 제공

#### 📊 상세 기록 관리 (10가지 유형)
- 🥛 **착유 기록** - 착유량, 유지방, 유단백, 체세포수 등
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

## 🏗️ 시스템 아키텍처

```
Flutter App (Client)
      ↕️ HTTP/REST API
FastAPI Server (Backend)
      ↕️ SDK
Firebase Firestore (Database)
      ↕️ CI/CD
AWS EC2 (Production)
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
  "record_date": "2025-06-15",
  "title": "착유 기록 (25.5L)",
  "description": "정상 착유",
  "record_data": {
    "milk_yield": 25.5,
    "fat_percentage": 3.8,
    "protein_percentage": 3.2,
    "somatic_cell_count": 150000
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
git clone https://github.com/SeulGi0117/blackcows-server.git
cd blackcows-server/backend

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

# Firebase 설정
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
```

### 3️⃣ Firebase 설정

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. Firestore Database 활성화
3. 서비스 계정 키 생성 및 다운로드
4. `.env` 파일에 Firebase 설정 추가

### 4️⃣ 서버 실행

```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5️⃣ API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API 엔드포인트

### 🔐 인증 API
| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/auth/register` | 회원가입 |
| `POST` | `/auth/login` | 로그인 |
| `POST` | `/auth/refresh` | 토큰 갱신 |
| `GET` | `/auth/me` | 내 정보 조회 |

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

### 🐮 젖소 상세정보 API
| Method | Endpoint | 설명 |
|--------|----------|------|
| `PUT` | `/cows/{cow_id}/details` | 상세정보 업데이트 |
| `GET` | `/cows/{cow_id}/details` | 상세정보 조회 |
| `GET` | `/cows/{cow_id}/has-details` | 상세정보 보유 여부 |

### 📝 상세 기록 관리 API
| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/detailed-records/milking` | 착유 기록 생성 |
| `POST` | `/detailed-records/estrus` | 발정 기록 생성 |
| `POST` | `/detailed-records/insemination` | 인공수정 기록 생성 |
| `POST` | `/detailed-records/pregnancy-check` | 임신감정 기록 생성 |
| `POST` | `/detailed-records/calving` | 분만 기록 생성 |
| `POST` | `/detailed-records/feed` | 사료급여 기록 생성 |
| `POST` | `/detailed-records/health-check` | 건강검진 기록 생성 |
| `POST` | `/detailed-records/vaccination` | 백신접종 기록 생성 |
| `POST` | `/detailed-records/weight` | 체중측정 기록 생성 |
| `POST` | `/detailed-records/treatment` | 치료 기록 생성 |
| `GET` | `/detailed-records/cow/{cow_id}` | 젖소별 기록 조회 |
| `GET` | `/detailed-records/{record_id}` | 기록 상세 조회 |
| `DELETE` | `/detailed-records/{record_id}` | 기록 삭제 |

### 📊 통계 및 분석 API
| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/detailed-records/cow/{cow_id}/milking/statistics` | 착유 통계 |
| `GET` | `/detailed-records/cow/{cow_id}/weight/trend` | 체중 변화 추이 |
| `GET` | `/detailed-records/cow/{cow_id}/reproduction/timeline` | 번식 타임라인 |
| `GET` | `/detailed-records/cow/{cow_id}/summary` | 젖소 기록 요약 |

## 💻 Flutter 앱 연동 예시

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

### 착유 기록 생성
```dart
Future<Map<String, dynamic>> createMilkingRecord(String cowId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/detailed-records/milking'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      'cow_id': cowId,
      'record_date': '2025-06-15',
      'milk_yield': 25.5,
      'fat_percentage': 3.8,
      'protein_percentage': 3.2,
      'somatic_cell_count': 150000,
      'milking_session': 1,
    }),
  );
  return json.decode(response.body);
}
```

## 🧪 테스트

### API 테스트 실행
```bash
# Python 테스트 스크립트 실행
python tests/api_test_examples.py

# 특정 테스트 실행
python -m pytest tests/test_cow_api.py
```

### Postman 테스트 컬렉션

1. **환경변수 설정**:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (로그인에서 받은 토큰)

2. **테스트 순서**:
   ```
   POST /auth/login → access_token 저장
   POST /cows/ → cow_id 저장
   PUT /cows/{{cow_id}}/details
   POST /detailed-records/milking
   GET /detailed-records/cow/{{cow_id}}
   ```

## 🚀 배포

### AWS EC2 자동 배포

GitHub Actions를 통한 자동 배포가 설정되어 있습니다:

1. **GitHub에 푸시** → 자동으로 EC2에 배포
2. **배포 과정**:
   - 코드 업데이트
   - 의존성 설치
   - 환경변수 설정
   - 서버 재시작
   - 헬스체크 확인

### 수동 배포

```bash
# EC2 서버 접속
ssh -i your-key.pem ubuntu@52.78.212.96

# 코드 업데이트
cd ~/blackcows-server
git pull

# 서버 재시작
sudo systemctl restart blackcows-server
```

## 🔧 데이터베이스 최적화

### 필수 Firestore 인덱스

Firebase Console에서 다음 복합 인덱스들을 설정해야 합니다:

1. **젖소 목록 조회용**:
   - `farm_id` (오름차순) + `is_active` (오름차순) + `created_at` (내림차순)

2. **즐겨찾기 조회용**:
   - `farm_id` (오름차순) + `is_favorite` (오름차순) + `is_active` (오름차순)

3. **상세 기록 조회용**:
   - `cow_id` (오름차순) + `farm_id` (오름차순) + `record_type` (오름차순) + `record_date` (내림차순)

4. **날짜별 기록 조회용**:
   - `farm_id` (오름차순) + `is_active` (오름차순) + `record_date` (내림차순)

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

### 3. 기록 관리 탭
- ✅ 10가지 상세 기록 유형별 입력 폼
- ✅ 날짜 선택기 및 유효성 검사
- ✅ 기록 목록 및 통계 화면

## 🛠️ 기술 스택

- **Backend**: FastAPI 0.115+, Python 3.11+
- **Database**: Firebase Firestore
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: AWS EC2, GitHub Actions
- **Documentation**: Swagger UI, ReDoc

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 있습니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

- **개발자**: SeulGi
