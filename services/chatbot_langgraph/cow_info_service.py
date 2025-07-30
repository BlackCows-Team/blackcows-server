import re
from config.firebase_config import get_firestore_client
from schemas.cow import HealthStatus, BreedingStatus, Temperament, MilkingBehavior

db = get_firestore_client()

def extract_ear_tag_number(text: str) -> str | None:
    """텍스트에서 12자리 이표번호 추출"""
    match = re.search(r'(\d{12})', text)
    if match:
        print(f"[DEBUG] 추출된 이표번호: {match.group(1)}")
        return match.group(1)
    else:
        print(f"[DEBUG] 이표번호 추출 실패: {text}")
        return None

def get_basic_info_by_ear_tag_number(ear_tag_number: str):
    """특정 젖소 - 기본 정보 조회"""
    try:
        docs = db.collection('cows').where("ear_tag_number", "==", ear_tag_number).limit(1).stream()
        cow_doc = next(docs, None)

        if cow_doc is None or not cow_doc.exists:
            print(f"[ERROR] 해당 이표번호로 문서를 찾지 못했습니다: {ear_tag_number}")
            return None

        cow_data = cow_doc.to_dict()
        print(f"[DEBUG] 조회된 cow ID: {cow_doc.id}, 데이터: {cow_data}")
        
        # HealthStatus와 BreedingStatus 안전하게 변환
        health_status = None
        if cow_data.get("health_status"):
            try:
                health_status = HealthStatus(cow_data["health_status"])
            except ValueError:
                print(f"[WARNING] 잘못된 health_status 값: {cow_data['health_status']} (젖소 ID: {cow_data['id']})")
                health_status = HealthStatus.NORMAL
        
        breeding_status = None
        if cow_data.get("breeding_status"):
            try:
                breeding_status = BreedingStatus(cow_data["breeding_status"])
            except ValueError:
                print(f"[WARNING] 잘못된 breeding_status 값: {cow_data['breeding_status']} (젖소 ID: {cow_data['id']})")
                breeding_status = None
        
        return {
            # 기본 정보
            "id": cow_data["id"],
            "ear_tag_number": cow_data["ear_tag_number"],
            "name": cow_data["name"],
            "birthdate": cow_data.get("birthdate"),
            "sensor_number": cow_data.get("sensor_number"),
            "health_status": health_status,
            "breeding_status": breeding_status,
            "breed": cow_data.get("breed"),
            "notes": cow_data.get("notes"),
            "is_favorite": cow_data.get("is_favorite", False),
            "farm_id": cow_data["farm_id"],
            "owner_id": cow_data["owner_id"],
            "created_at": cow_data["created_at"],
            "updated_at": cow_data["updated_at"],
            "is_active": cow_data["is_active"]
        }
        
    except Exception as e:
        print(f"[ERROR] 특정 젖소 *기본 정보* 조회 전체 실패 (ear_tag_number: {ear_tag_number}): {str(e)}")
        return None
    

def get_cow_details_by_ear_tag_number(ear_tag_number: str):
    """특정 젖소 - 상세 정보 조회"""
    try:
        cow_doc = db.collection('cows').document(ear_tag_number).get()
        
        if not cow_doc.exists:
            return None
        
        cow_data = cow_doc.to_dict()
        
        # 상세 정보 추출
        detailed_info = cow_data.get("detailed_info", {})

        body_info = detailed_info.get("body_info", {})
        production_info = detailed_info.get("production_info", {})
        breeding_info = detailed_info.get("breeding_info", {})
        health_info = detailed_info.get("health_info", {})
        management_info = detailed_info.get("management_info", {})
        pedigree_info = detailed_info.get("pedigree_info", {})
        feed_info = detailed_info.get("feed_info", {})
        location_info = detailed_info.get("location_info", {})
        behavioral_info = detailed_info.get("behavioral_info", {})
        
        return {
            "has_detailed_info": cow_data.get("has_detailed_info", False),
            "detail_updated_at": cow_data.get("detail_updated_at"),

            "body_info": {
                "weight": body_info.get("weight"),
                "height": body_info.get("height"),
                "body_length": body_info.get("body_length"),
                "chest_girth": body_info.get("chest_girth"),
                "body_condition_score": body_info.get("body_condition_score"),
            },
            "production_info": {
                "lactation_number": production_info.get("lactation_number"),
                "milk_yield_record": production_info.get("milk_yield_record"),
                "lifetime_milk_yield": production_info.get("lifetime_milk_yield"),
                "average_daily_yield": production_info.get("average_daily_yield"),
            },
            "breeding_info": {
                "first_calving_date": breeding_info.get("first_calving_date"),
                "last_calving_date": breeding_info.get("last_calving_date"),
                "total_calves": breeding_info.get("total_calves"),
                "breeding_efficiency": breeding_info.get("breeding_efficiency"),
            },
            "health_info": {
                "vaccination_status": health_info.get("vaccination_status"),
                "last_health_check": health_info.get("last_health_check"),
                "chronic_conditions": health_info.get("chronic_conditions"),
                "allergy_info": health_info.get("allergy_info"),
            },
            "management_info": {
                "purchase_date": management_info.get("purchase_date"),
                "purchase_price": management_info.get("purchase_price"),
                "current_value": management_info.get("current_value"),
                "insurance_policy": management_info.get("insurance_policy"),
                "special_management": management_info.get("special_management"),
            },
            "pedigree_info": {
                "mother_id": pedigree_info.get("mother_id"),
                "father_info": pedigree_info.get("father_info"),
                "genetic_info": pedigree_info.get("genetic_info"),
            },
            "feed_info": {
                "feed_type": feed_info.get("feed_type"),
                "daily_feed_amount": feed_info.get("daily_feed_amount"),
                "supplement_info": feed_info.get("supplement_info"),
            },
            "location_info": {
                "barn_section": location_info.get("barn_section"),
                "stall_number": location_info.get("stall_number"),
            },
            "behavioral_info": {
                "temperament": Temperament(behavioral_info["temperament"]) if behavioral_info.get("temperament") else None,
                "milking_behavior": MilkingBehavior(behavioral_info["milking_behavior"]) if behavioral_info.get("milking_behavior") else None,
                "retirement_plan": behavioral_info.get("retirement_plan"),
            },
        }
        
    except Exception as e:
        # 실패 시에도 500 오류 방지
        print(f"[ERROR] 특정 젖소 *상세 정보* 조회 전체 실패 (ear_tag_number: {ear_tag_number}): {str(e)}")
        return None

def build_relevant_cow_info_by_category(category: str, basic: dict, detail: dict) -> dict:
    """선택된 카테고리 기준으로 소 정보 요약을 생성"""

    if not basic or not detail:
        return {"오류": "해당 소의 기본 정보 또는 상세 정보를 찾을 수 없습니다."}

    # 공통 기본 정보
    info = {
        "이름": basic.get("name", "미등록"),
        "이표번호": basic.get("ear_tag_number", "미등록"),
        "출생일": basic.get("birthdate", "미등록"),
        "건강 상태": basic.get("health_status", {}).get("name") if isinstance(basic.get("health_status"), dict) else str(basic.get("health_status", "")),
        "번식 상태": basic.get("breeding_status", {}).get("name") if isinstance(basic.get("breeding_status"), dict) else str(basic.get("breeding_status", "")),
    }

    # 카테고리별 필드 정의
    fields_by_category = {
        "body_info": ["weight", "height", "body_length", "chest_girth", "body_condition_score"],
        "production_info": ["lactation_number", "milk_yield_record", "lifetime_milk_yield", "average_daily_yield"],
        "breeding_info": ["first_calving_date", "last_calving_date", "total_calves", "breeding_efficiency"],
        "health_info": ["vaccination_status", "last_health_check", "chronic_conditions", "allergy_info"],
        "management_info": ["purchase_date", "purchase_price", "current_value", "insurance_policy", "special_management"],
        "pedigree_info": ["mother_id", "father_info", "genetic_info"],
        "feed_info": ["feed_type", "daily_feed_amount", "supplement_info"],
        "location_info": ["barn_section", "stall_number"],
        "behavioral_info": ["temperament", "milking_behavior", "retirement_plan"]
    }

    if category not in fields_by_category:
        return {"오류": f"카테고리 '{category}'는 지원하지 않습니다."}

    category_data = detail.get(category, {})
    for field in fields_by_category[category]:
        value = category_data.get(field)
        if value:
            info[field] = str(value)

    return info
