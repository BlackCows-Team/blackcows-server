"""
젖소 관리 및 기록 관리 API 테스트 예시
Postman 또는 Python requests를 사용한 테스트 코드
"""

import requests
import json
from datetime import datetime, timedelta

# API 기본 설정
BASE_URL = "http://localhost:8000"  # 로컬 개발 환경
# BASE_URL = "https://your-api-domain.com"  # 배포 환경

class APITestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None
        self.farm_id = None
        self.user_id = None
    
    def login(self, email: str, password: str):
        """로그인 테스트"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.farm_id = data.get("user", {}).get("farm_id")
            self.user_id = data.get("user", {}).get("id")
            print("✅ 로그인 성공")
            return data
        else:
            print(f"❌ 로그인 실패: {response.text}")
            return None
    
    def get_headers(self):
        """인증 헤더 생성"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    # ===========================================
    # 젖소 관리 API 테스트
    # ===========================================
    
    def test_register_cow(self):
        """젖소 등록 테스트"""
        print("\n=== 젖소 등록 테스트 ===")
        
        cow_data = {
            "ear_tag_number": "002123456789",
            "name": "테스트소1",
            "birthdate": "2022-03-15",
            "sensor_number": "1234567890123",
            "health_status": "good",
            "breeding_status": "lactating",
            "breed": "Holstein",
            "notes": "테스트용 젖소"
        }
        
        response = requests.post(
            f"{self.base_url}/cows/",
            headers=self.get_headers(),
            json=cow_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 젖소 등록 성공: {data['name']} (ID: {data['id']})")
            return data
        else:
            print(f"❌ 젖소 등록 실패: {response.text}")
            return None
    
    def test_get_cows(self):
        """젖소 목록 조회 테스트"""
        print("\n=== 젖소 목록 조회 테스트 ===")
        
        response = requests.get(
            f"{self.base_url}/cows/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 젖소 목록 조회 성공: {len(data)}마리")
            return data
        else:
            print(f"❌ 젖소 목록 조회 실패: {response.text}")
            return None
    
    def test_toggle_favorite(self, cow_id: str):
        """즐겨찾기 토글 테스트"""
        print("\n=== 즐겨찾기 토글 테스트 ===")
        
        response = requests.post(
            f"{self.base_url}/cows/{cow_id}/favorite",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 즐겨찾기 토글 성공: {data['message']}")
            return data
        else:
            print(f"❌ 즐겨찾기 토글 실패: {response.text}")
            return None
    
    def test_get_favorite_cows(self):
        """즐겨찾기 젖소 목록 조회 테스트"""
        print("\n=== 즐겨찾기 젖소 목록 조회 테스트 ===")
        
        response = requests.get(
            f"{self.base_url}/cows/favorites/list",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 즐겨찾기 젖소 조회 성공: {len(data)}마리")
            return data
        else:
            print(f"❌ 즐겨찾기 젖소 조회 실패: {response.text}")
            return None
    
    # ===========================================
    # 기록 관리 API 테스트
    # ===========================================
    
    def test_create_breeding_record(self, cow_id: str):
        """번식기록 생성 테스트"""
        print("\n=== 번식기록 생성 테스트 ===")
        
        today = datetime.now().strftime("%Y-%m-%d")
        calving_date = (datetime.now() + timedelta(days=280)).strftime("%Y-%m-%d")
        
        record_data = {
            "cow_id": cow_id,
            "record_date": today,
            "title": "인공수정 실시",
            "description": "정기 인공수정 실시",
            "breeding_method": "artificial",
            "breeding_date": today,
            "bull_info": "홀스타인 우수 종축",
            "expected_calving_date": calving_date,
            "breeding_result": "pending",
            "cost": 50000,
            "veterinarian": "김수의사"
        }
        
        response = requests.post(
            f"{self.base_url}/records/breeding",
            headers=self.get_headers(),
            json=record_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 번식기록 생성 성공: {data['title']} (ID: {data['id']})")
            return data
        else:
            print(f"❌ 번식기록 생성 실패: {response.text}")
            return None
    
    def test_create_disease_record(self, cow_id: str):
        """질병기록 생성 테스트"""
        print("\n=== 질병기록 생성 테스트 ===")
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        record_data = {
            "cow_id": cow_id,
            "record_date": today,
            "title": "유방염 치료",
            "description": "좌측 전유방 염증 발견",
            "disease_name": "유방염",
            "symptoms": "유방 부종, 발열, 우유 이상",
            "severity": "moderate",
            "treatment_content": "항생제 투여 및 관찰",
            "treatment_start_date": today,
            "treatment_status": "ongoing",
            "treatment_cost": 80000,
            "veterinarian": "박수의사",
            "medication": "페니실린"
        }
        
        response = requests.post(
            f"{self.base_url}/records/disease",
            headers=self.get_headers(),
            json=record_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 질병기록 생성 성공: {data['title']} (ID: {data['id']})")
            return data
        else:
            print(f"❌ 질병기록 생성 실패: {response.text}")
            return None
    
    def test_create_status_change_record(self, cow_id: str):
        """분류변경 기록 생성 테스트"""
        print("\n=== 분류변경 기록 생성 테스트 ===")
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        record_data = {
            "cow_id": cow_id,
            "record_date": today,
            "title": "번식상태 변경",
            "description": "임신 확인으로 인한 상태 변경",
            "previous_status": "breeding",
            "new_status": "pregnant",
            "change_reason": "임신 확인됨",
            "change_date": today,
            "responsible_person": "농장관리자"
        }
        
        response = requests.post(
            f"{self.base_url}/records/status-change",
            headers=self.get_headers(),
            json=record_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 분류변경 기록 생성 성공: {data['title']} (ID: {data['id']})")
            return data
        else:
            print(f"❌ 분류변경 기록 생성 실패: {response.text}")
            return None
    
    def test_create_other_record(self, cow_id: str):
        """기타기록 생성 테스트"""
        print("\n=== 기타기록 생성 테스트 ===")
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        record_data = {
            "cow_id": cow_id,
            "record_date": today,
            "title": "체중 측정",
            "description": "정기 체중 측정 실시",
            "category": "measurement",
            "details": {
                "weight": "450kg",
                "body_condition_score": "3.5",
                "measurement_method": "전자저울"
            },
            "importance": "normal"
        }
        
        response = requests.post(
            f"{self.base_url}/records/other",
            headers=self.get_headers(),
            json=record_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 기타기록 생성 성공: {data['title']} (ID: {data['id']})")
            return data
        else:
            print(f"❌ 기타기록 생성 실패: {response.text}")
            return None
    
    def test_get_cow_records(self, cow_id: str):
        """젖소 기록 목록 조회 테스트"""
        print("\n=== 젖소 기록 목록 조회 테스트 ===")
        
        response = requests.get(
            f"{self.base_url}/records/cow/{cow_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 젖소 기록 조회 성공: {len(data)}개 기록")
            return data
        else:
            print(f"❌ 젖소 기록 조회 실패: {response.text}")
            return None
    
    def test_get_record_statistics(self):
        """기록 통계 조회 테스트"""
        print("\n=== 기록 통계 조회 테스트 ===")
        
        response = requests.get(
            f"{self.base_url}/records/statistics/summary",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 기록 통계 조회 성공: 총 {data.get('total_records', 0)}개 기록")
            print(f"   - 번식기록: {data.get('record_type_statistics', {}).get('breeding', 0)}개")
            print(f"   - 질병기록: {data.get('record_type_statistics', {}).get('disease', 0)}개")
            print(f"   - 분류변경: {data.get('record_type_statistics', {}).get('status_change', 0)}개")
            print(f"   - 기타기록: {data.get('record_type_statistics', {}).get('other', 0)}개")
            return data
        else:
            print(f"❌ 기록 통계 조회 실패: {response.text}")
            return None

def run_full_test():
    """전체 API 테스트 실행"""
    print("🚀 젖소 관리 & 기록 관리 API 테스트 시작")
    print("=" * 50)
    
    # 테스트 클라이언트 초기화
    client = APITestClient(BASE_URL)
    
    # 1. 로그인 테스트
    login_result = client.login("test@farm.com", "password123")
    if not login_result:
        print("❌ 로그인 실패로 테스트 중단")
        return
    
    # 2. 젖소 등록 테스트
    cow = client.test_register_cow()
    if not cow:
        print("❌ 젖소 등록 실패로 테스트 중단")
        return
    
    cow_id = cow["id"]
    
    # 3. 젖소 목록 조회 테스트
    client.test_get_cows()
    
    # 4. 즐겨찾기 토글 테스트
    client.test_toggle_favorite(cow_id)
    
    # 5. 즐겨찾기 목록 조회 테스트
    client.test_get_favorite_cows()
    
    # 6. 기록 생성 테스트들
    client.test_create_breeding_record(cow_id)
    client.test_create_disease_record(cow_id)
    client.test_create_status_change_record(cow_id)
    client.test_create_other_record(cow_id)
    
    # 7. 젖소별 기록 조회 테스트
    client.test_get_cow_records(cow_id)
    
    # 8. 기록 통계 조회 테스트
    client.test_get_record_statistics()
    
    print("\n" + "=" * 50)
    print("🎉 전체 API 테스트 완료!")

if __name__ == "__main__":
    run_full_test()

"""
Postman을 사용한 테스트 컬렉션 예시:

1. 환경 변수 설정:
   - base_url: http://localhost:8000
   - access_token: {{로그인에서 받은 토큰}}

2. 테스트 순서:
   - POST /auth/login → access_token 저장
   - POST /cows/ → cow_id 저장
   - POST /cows/{{cow_id}}/favorite
   - GET /cows/favorites/list
   - POST /records/breeding
   - POST /records/disease
   - GET /records/cow/{{cow_id}}
   - GET /records/statistics/summary

3. Pre-request Script 예시:
```javascript
// 로그인이 필요한 API에 자동으로 토큰 추가
if (pm.environment.get("access_token")) {
    pm.request.headers.add({
        key: "Authorization",
        value: "Bearer " + pm.environment.get("access_token")
    });
}
```

4. Test Script 예시:
```javascript
// 응답 상태 코드 검증
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// 응답 JSON 검증
pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("id");
    pm.expect(jsonData).to.have.property("name");
});
```
"""