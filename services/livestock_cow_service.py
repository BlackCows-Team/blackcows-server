# services/livestock_cow_service.py

from datetime import datetime
from typing import Dict, Optional
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.cow import HealthStatus, BreedingStatus
import uuid
import httpx
import xml.etree.ElementTree as ET
import os

class LivestockCowService:
    # 메모리 캐싱 
    _cache = {}  # 결과 저장
    _cache_time = {}  # 언제 저장했는지 기록
    
    @staticmethod
    async def check_registration_status(ear_tag_number: str, farm_id: str) -> Dict:
        """
        젖소 등록 상태 확인
        
        1. 이미 등록된 젖소인지 확인 (전체 시스템에서)
        2. 축산물이력제에서 조회 가능한지 확인
        3. 상태에 따른 응답 반환
        """
        try:
            db = get_firestore_client()
            
            # 1. 이미 등록된 젖소인지 확인 (전체 시스템에서)
            existing_cow_query = db.collection('cows')\
                .where('ear_tag_number', '==', ear_tag_number)\
                .where('is_active', '==', True)\
                .get()
            
            if existing_cow_query:
                existing_cow = existing_cow_query[0].to_dict()
                existing_farm_id = existing_cow.get("farm_id")
                
                # 같은 농장인지 다른 농장인지 확인
                if existing_farm_id == farm_id:
                    message = f"이표번호 '{ear_tag_number}'은 이미 등록된 젖소입니다"
                else:
                    message = f"이표번호 '{ear_tag_number}'은 이미 다른 농장에서 등록되어 있습니다"
                
                return {
                    "status": "already_registered",
                    "ear_tag_number": ear_tag_number,
                    "message": message,
                    "existing_cow_info": {
                        "id": existing_cow["id"],
                        "name": existing_cow["name"],
                        "ear_tag_number": existing_cow["ear_tag_number"],
                        "birthdate": existing_cow.get("birthdate"),
                        "breed": existing_cow.get("breed"),
                        "farm_id": existing_farm_id,
                        "created_at": existing_cow["created_at"].isoformat() if existing_cow.get("created_at") else None
                    }
                }
            
            # 2. 축산물이력제에서 조회 시도
            livestock_data = await LivestockCowService._fetch_livestock_trace_data(ear_tag_number)
            
            if livestock_data and livestock_data.get("basic_info"):
                return {
                    "status": "livestock_trace_available",
                    "ear_tag_number": ear_tag_number,
                    "message": "축산물이력제에서 젖소 정보를 찾았습니다",
                    "livestock_trace_data": livestock_data
                }
            else:
                return {
                    "status": "manual_registration_required", 
                    "ear_tag_number": ear_tag_number,
                    "message": "축산물이력제에서 젖소 정보를 찾을 수 없습니다. 수동으로 등록해주세요"
                }
                
        except Exception as e:
            print(f"[ERROR] 등록 상태 확인 중 오류: {str(e)}")
            return {
                "status": "error",
                "ear_tag_number": ear_tag_number,
                "message": f"등록 상태 확인 중 오류가 발생했습니다: {str(e)}"
            }
    
    @staticmethod
    async def register_cow_from_livestock_trace(
        ear_tag_number: str, 
        user_provided_name: str, 
        user: Dict,
        sensor_number: Optional[str] = None,
        additional_notes: Optional[str] = None
    ) -> Dict:
        """
        축산물이력제 정보를 기반으로 젖소 등록
        
        1. 축산물이력제에서 젖소 정보 조회
        2. 조회된 정보를 우리 DB 스키마에 맞게 변환
        3. Firebase에 젖소 정보 저장
        """
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 1. 중복 확인 (전체 시스템에서)
            existing_cow_query = db.collection('cows')\
                .where('ear_tag_number', '==', ear_tag_number)\
                .where('is_active', '==', True)\
                .get()
            
            if existing_cow_query:
                existing_cow = existing_cow_query[0].to_dict()
                existing_farm_id = existing_cow.get("farm_id")
                
                if existing_farm_id == farm_id:
                    detail_message = f"이표번호 '{ear_tag_number}'는 이미 등록되어 있습니다"
                else:
                    detail_message = f"이표번호 '{ear_tag_number}'는 이미 다른 농장에서 등록되어 있습니다"
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail_message
                )
            
            # 2. 센서 번호 중복 확인 (제공된 경우)
            if sensor_number:
                existing_sensor_query = db.collection('cows')\
                    .where('farm_id', '==', farm_id)\
                    .where('sensor_number', '==', sensor_number)\
                    .where('is_active', '==', True)\
                    .get()
                
                if existing_sensor_query:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"센서 번호 '{sensor_number}'는 이미 사용 중입니다"
                    )
            
            # 3. 축산물이력제에서 젖소 정보 조회
            livestock_data = await LivestockCowService._fetch_livestock_trace_data(ear_tag_number)
            
            if not livestock_data or not livestock_data.get("basic_info"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="축산물이력제에서 젖소 정보를 찾을 수 없습니다"
                )
            
            # 4. 축산물이력제 데이터를 우리 스키마에 맞게 변환
            cow_data = LivestockCowService._convert_livestock_data_to_cow(
                livestock_data, 
                user_provided_name, 
                sensor_number,
                additional_notes
            )
            
            # 5. 젖소 ID 생성 및 메타데이터 추가
            cow_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            cow_document = {
                "id": cow_id,
                **cow_data,
                "is_favorite": False,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True,
                # 축산물이력제 연동 정보 저장
                "livestock_trace_data": livestock_data,
                "registered_from_livestock_trace": True,
                "livestock_trace_registered_at": current_time
            }
            
            # 6. Firebase에 저장
            db.collection('cows').document(cow_id).set(cow_document)
            
            # 7. 성공 응답
            return {
                "success": True,
                "message": f"젖소 '{user_provided_name}' (이표번호: {ear_tag_number})가 축산물이력제 정보로 성공적으로 등록되었습니다",
                "cow_id": cow_id,
                "cow_info": {
                    "id": cow_id,
                    "name": user_provided_name,
                    "ear_tag_number": ear_tag_number,
                    "birthdate": cow_data.get("birthdate"),
                    "breed": cow_data.get("breed"),
                    "sensor_number": sensor_number,
                    "notes": additional_notes
                },
                "livestock_trace_data": livestock_data
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            print(f"[ERROR] 축산물이력제 기반 젖소 등록 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"젖소 등록 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    async def _fetch_livestock_trace_data(ear_tag_number: str) -> Optional[Dict]:
        """축산물이력제 API에서 젖소 정보 조회"""
        try:
            # 캐시 확인 (5분간 유효)
            current_time = datetime.utcnow()
            if ear_tag_number in LivestockCowService._cache:
                cached_time = LivestockCowService._cache_time[ear_tag_number]
                time_diff = (current_time - cached_time).total_seconds()
                
                if time_diff < 300:  # 5분
                    print(f"[캐시 사용] 이표번호 {ear_tag_number}")
                    return LivestockCowService._cache[ear_tag_number]
                else:
                    # 오래된 캐시 삭제
                    del LivestockCowService._cache[ear_tag_number]
                    del LivestockCowService._cache_time[ear_tag_number]
            
            print(f"[API 호출] 이표번호 {ear_tag_number}")
            
            service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
            if not service_key:
                print("[ERROR] 축산물이력제 API 키가 설정되지 않았습니다")
                return None
            
            base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
            
            # 기본 개체정보만 조회 (가장 중요한 정보)
            basic_info = await LivestockCowService._fetch_livestock_api(
                base_url, service_key, ear_tag_number, "1"
            )
            
            if not basic_info:
                return None
            
            # 기본 정보 파싱
            parsed_basic_info = LivestockCowService._parse_basic_info(basic_info, ear_tag_number)
            
            result = {
                "basic_info": parsed_basic_info,
                "ear_tag_number": ear_tag_number,
                "api_response_time": current_time.isoformat()
            }
            
            # 캐시에 저장
            LivestockCowService._cache[ear_tag_number] = result
            LivestockCowService._cache_time[ear_tag_number] = current_time
            print(f"[캐시 저장] 이표번호 {ear_tag_number}")
            
            return result
            
        except Exception as e:
            print(f"[ERROR] 축산물이력제 API 조회 실패: {str(e)}")
            return None
    
    @staticmethod
    async def _fetch_livestock_api(base_url: str, service_key: str, ear_tag_number: str, option_no: str):
        """축산물이력제 API 호출"""
        try:
            import urllib.parse
            
            if '%' in service_key:
                decoded_service_key = urllib.parse.unquote(service_key)
            else:
                decoded_service_key = service_key
            
            params = {
                "serviceKey": decoded_service_key,
                "traceNo": ear_tag_number,
                "optionNo": option_no
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params, timeout=30.0)
                
                if response.status_code != 200:
                    return None
                
                try:
                    root = ET.fromstring(response.text)
                except ET.ParseError:
                    return None
                
                # 응답 상태 확인
                header = root.find('header')
                if header is not None:
                    result_code = header.find('resultCode')
                    if result_code is not None and result_code.text != "00":
                        return None
                
                # 데이터 추출
                items = root.find('.//items')
                if items is None:
                    return None
                    
                item_elements = items.findall('item')
                if len(item_elements) == 0:
                    return None
                
                item_list = []
                for item in item_elements:
                    item_data = {}
                    for element in item:
                        if element.text:
                            item_data[element.tag] = element.text.strip()
                    item_list.append(item_data)
                    
                return item_list
                
        except Exception as e:
            print(f"[ERROR] API 호출 오류: {str(e)}")
            return None
    
    @staticmethod
    def _parse_basic_info(items: list, ear_tag_number: str) -> Dict:
        """기본 개체정보 파싱"""
        if not items:
            return {"ear_tag_number": ear_tag_number}
        
        item = items[0]
        
        # 출생일 파싱 및 개월령 계산
        birth_date = None
        age_months = None
        if item.get('birthYmd') and len(item['birthYmd']) == 8:
            birth_date = f"{item['birthYmd'][:4]}-{item['birthYmd'][4:6]}-{item['birthYmd'][6:8]}"
            try:
                birth_datetime = datetime.strptime(birth_date, '%Y-%m-%d')
                today = datetime.now()
                age_months = (today.year - birth_datetime.year) * 12 + (today.month - birth_datetime.month)
                if age_months < 0:
                    age_months = 0
            except:
                pass
        
        return {
            "cattle_no": item.get('cattleNo'),
            "ear_tag_number": ear_tag_number,
            "birth_date": birth_date,
            "age_months": age_months,
            "breed": item.get('lsTypeNm'),
            "gender": item.get('sexNm'),
            "import_elapsed_months": int(item['monthDiff']) if item.get('monthDiff') and item['monthDiff'].isdigit() else None,
            "import_country": item.get('nationNm'),
            "farm_unique_no": item.get('farmUniqueNo'),
            "farm_no": item.get('farmNo')
        }
    
    @staticmethod
    def _convert_livestock_data_to_cow(
        livestock_data: Dict, 
        user_provided_name: str,
        sensor_number: Optional[str] = None,
        additional_notes: Optional[str] = None
    ) -> Dict:
        """
        축산물이력제 데이터를 우리 젖소 스키마에 맞게 변환
        """
        basic_info = livestock_data.get("basic_info", {})
        
        # 품종 매핑
        breed_mapping = {
            "홀스타인": "Holstein",
            "젖소": "Holstein", 
            "한우": "Korean Native",
            "육우": "Beef Cattle"
        }
        
        original_breed = basic_info.get("breed", "")
        mapped_breed = breed_mapping.get(original_breed, original_breed)
        
        # 성별에 따른 기본 번식상태 설정
        gender = basic_info.get("gender", "")
        if "암" in gender or "Female" in gender:
            # 나이에 따른 번식상태 추정
            age_months = basic_info.get("age_months", 0)
            if age_months and age_months < 12:
                breeding_status = BreedingStatus.CALF.value
            elif age_months and age_months < 24:
                breeding_status = BreedingStatus.HEIFER.value
            else:
                breeding_status = BreedingStatus.LACTATING.value  # 기본값
        else:
            breeding_status = None  # 수소는 번식상태 없음
        
        # 메모 구성
        notes_parts = []
        if additional_notes:
            notes_parts.append(additional_notes)
        
        # 축산물이력제 추가 정보를 메모에 포함
        livestock_info_parts = []
        if basic_info.get("cattle_no"):
            livestock_info_parts.append(f"개체번호: {basic_info['cattle_no']}")
        if basic_info.get("gender"):
            livestock_info_parts.append(f"성별: {basic_info['gender']}")
        if basic_info.get("farm_no"):
            livestock_info_parts.append(f"농장번호: {basic_info['farm_no']}")
        if basic_info.get("import_country"):
            livestock_info_parts.append(f"수입국: {basic_info['import_country']}")
        
        if livestock_info_parts:
            notes_parts.append(f"[축산물이력제 정보] {', '.join(livestock_info_parts)}")
        
        final_notes = " | ".join(notes_parts) if notes_parts else None
        
        return {
            "ear_tag_number": basic_info.get("ear_tag_number"),
            "name": user_provided_name,
            "birthdate": basic_info.get("birth_date"),
            "sensor_number": sensor_number,
            "health_status": HealthStatus.NORMAL.value,  # 기본값: 정상
            "breeding_status": breeding_status,
            "breed": mapped_breed,
            "notes": final_notes
        }