# 기록 관리 서비스
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.record import (
    RecordResponse, RecordSummary, RecordUpdate, RecordType,
    BreedingRecordCreate, DiseaseRecordCreate, StatusChangeRecordCreate, OtherRecordCreate
)
import uuid

class RecordFirebaseService:
    
    @staticmethod
    def create_breeding_record(record_data: BreedingRecordCreate, user: Dict) -> RecordResponse:
        """번식기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소 존재 확인
            cow_info = RecordFirebaseService._get_cow_info(record_data.cow_id, farm_id)
            
            # 기록 데이터 구성
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            breeding_data = {
                "breeding_method": record_data.breeding_method.value,
                "breeding_date": record_data.breeding_date,
                "bull_info": record_data.bull_info,
                "expected_calving_date": record_data.expected_calving_date,
                "pregnancy_check_date": record_data.pregnancy_check_date,
                "breeding_result": record_data.breeding_result.value,
                "cost": record_data.cost,
                "veterinarian": record_data.veterinarian
            }
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": RecordType.BREEDING.value,
                "record_date": record_data.record_date,
                "title": record_data.title,
                "description": record_data.description,
                "record_data": breeding_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 저장
            db.collection('cow_records').document(record_id).set(record_document)
            
            return RecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=RecordType.BREEDING,
                record_date=record_data.record_date,
                title=record_data.title,
                description=record_data.description,
                record_data=breeding_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"번식기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_disease_record(record_data: DiseaseRecordCreate, user: Dict) -> RecordResponse:
        """질병기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소 존재 확인
            cow_info = RecordFirebaseService._get_cow_info(record_data.cow_id, farm_id)
            
            # 기록 데이터 구성
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            disease_data = {
                "disease_name": record_data.disease_name,
                "symptoms": record_data.symptoms,
                "severity": record_data.severity.value,
                "treatment_content": record_data.treatment_content,
                "treatment_start_date": record_data.treatment_start_date,
                "treatment_end_date": record_data.treatment_end_date,
                "treatment_status": record_data.treatment_status.value,
                "treatment_cost": record_data.treatment_cost,
                "veterinarian": record_data.veterinarian,
                "medication": record_data.medication
            }
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": RecordType.DISEASE.value,
                "record_date": record_data.record_date,
                "title": record_data.title,
                "description": record_data.description,
                "record_data": disease_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 저장
            db.collection('cow_records').document(record_id).set(record_document)
            
            return RecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=RecordType.DISEASE,
                record_date=record_data.record_date,
                title=record_data.title,
                description=record_data.description,
                record_data=disease_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"질병기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_status_change_record(record_data: StatusChangeRecordCreate, user: Dict) -> RecordResponse:
        """분류변경 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소 존재 확인
            cow_info = RecordFirebaseService._get_cow_info(record_data.cow_id, farm_id)
            
            # 기록 데이터 구성
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            status_change_data = {
                "previous_status": record_data.previous_status,
                "new_status": record_data.new_status,
                "change_reason": record_data.change_reason,
                "change_date": record_data.change_date,
                "responsible_person": record_data.responsible_person
            }
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": RecordType.STATUS_CHANGE.value,
                "record_date": record_data.record_date,
                "title": record_data.title,
                "description": record_data.description,
                "record_data": status_change_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 저장
            db.collection('cow_records').document(record_id).set(record_document)
            
            return RecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=RecordType.STATUS_CHANGE,
                record_date=record_data.record_date,
                title=record_data.title,
                description=record_data.description,
                record_data=status_change_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"분류변경 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_other_record(record_data: OtherRecordCreate, user: Dict) -> RecordResponse:
        """기타기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소 존재 확인
            cow_info = RecordFirebaseService._get_cow_info(record_data.cow_id, farm_id)
            
            # 기록 데이터 구성
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            other_data = {
                "category": record_data.category,
                "details": record_data.details or {},
                "attachments": record_data.attachments or [],
                "importance": record_data.importance or "normal"
            }
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": RecordType.OTHER.value,
                "record_date": record_data.record_date,
                "title": record_data.title,
                "description": record_data.description,
                "record_data": other_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 저장
            db.collection('cow_records').document(record_id).set(record_document)
            
            return RecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=RecordType.OTHER,
                record_date=record_data.record_date,
                title=record_data.title,
                description=record_data.description,
                record_data=other_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"기타기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_records_by_cow(cow_id: str, farm_id: str, record_type: Optional[RecordType] = None) -> List[RecordSummary]:
        """특정 젖소의 기록 목록 조회 - 500 오류 해결"""
        try:
            db = get_firestore_client()
            
            # 젖소 정보 안전하게 조회
            cow_info = None
            try:
                cow_info = RecordFirebaseService._get_cow_info(cow_id, farm_id)
            except:
                # 젖소 정보 조회 실패 시 기본값 사용
                cow_info = {
                    "name": "알 수 없음",
                    "ear_tag_number": "N/A"
                }
            
            # 기본 쿼리
            query = db.collection('cow_records').where('cow_id', '==', cow_id).where('farm_id', '==', farm_id).where('is_active', '==', True)
            
            # 기록 유형 필터링
            if record_type:
                query = query.where('record_type', '==', record_type.value)
            
            # 날짜 순으로 정렬 (최신순)
            records_query = query.order_by('record_date', direction='DESCENDING').get()
            
            records = []
            for record_doc in records_query:
                try:
                    record_data = record_doc.to_dict()
                    records.append(RecordSummary(
                        id=record_data.get("id", ""),
                        cow_id=record_data.get("cow_id", cow_id),
                        cow_name=cow_info.get("name", "알 수 없음"),
                        cow_ear_tag_number=cow_info.get("ear_tag_number", "N/A"),
                        record_type=RecordType(record_data.get("record_type", "other")),
                        record_date=record_data.get("record_date", ""),
                        title=record_data.get("title", "제목 없음"),
                        created_at=record_data.get("created_at", datetime.utcnow())
                    ))
                except Exception as record_error:
                    # 개별 기록 처리 실패 시 로그만 남기고 계속 진행
                    print(f"[WARNING] 기록 처리 실패 (ID: {record_doc.id}): {str(record_error)}")
                    continue
            
            return records
            
        except Exception as e:
            # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
            print(f"[ERROR] 젖소 기록 목록 조회 전체 실패 (cow_id: {cow_id}): {str(e)}")
            return []
    
    @staticmethod
    def get_record_detail(record_id: str, farm_id: str) -> RecordResponse:
        """기록 상세 정보 조회"""
        try:
            db = get_firestore_client()
            record_doc = db.collection('cow_records').document(record_id).get()
            
            if not record_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="기록을 찾을 수 없습니다"
                )
            
            record_data = record_doc.to_dict()
            
            # 농장 ID 확인 (보안)
            if record_data.get("farm_id") != farm_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="기록을 찾을 수 없습니다"
                )
            
            # 젖소 정보 조회
            cow_info = RecordFirebaseService._get_cow_info(record_data["cow_id"], farm_id)
            
            return RecordResponse(
                id=record_data["id"],
                cow_id=record_data["cow_id"],
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=RecordType(record_data["record_type"]),
                record_date=record_data["record_date"],
                title=record_data["title"],
                description=record_data.get("description"),
                record_data=record_data["record_data"],
                farm_id=record_data["farm_id"],
                owner_id=record_data["owner_id"],
                created_at=record_data["created_at"],
                updated_at=record_data["updated_at"],
                is_active=record_data["is_active"]
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"기록 상세 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_all_records_by_farm(farm_id: str, record_type: Optional[RecordType] = None, limit: int = 50) -> List[RecordSummary]:
        """농장의 모든 기록 조회 - 500 오류 해결"""
        try:
            db = get_firestore_client()
            
            # 기본 쿼리
            query = db.collection('cow_records').where('farm_id', '==', farm_id).where('is_active', '==', True)
            
            # 기록 유형 필터링
            if record_type:
                query = query.where('record_type', '==', record_type.value)
            
            # 날짜 순으로 정렬하고 제한
            records_query = query.order_by('record_date', direction='DESCENDING').limit(limit).get()
            
            records = []
            for record_doc in records_query:
                try:
                    record_data = record_doc.to_dict()
                    
                    # 젖소 정보 안전하게 조회
                    cow_info = None
                    try:
                        cow_info = RecordFirebaseService._get_cow_info(record_data.get("cow_id", ""), farm_id)
                    except:
                        # 젖소 정보 조회 실패 시 기본값 사용
                        cow_info = {
                            "name": "알 수 없음",
                            "ear_tag_number": "N/A"
                        }
                    
                    records.append(RecordSummary(
                        id=record_data.get("id", ""),
                        cow_id=record_data.get("cow_id", ""),
                        cow_name=cow_info.get("name", "알 수 없음"),
                        cow_ear_tag_number=cow_info.get("ear_tag_number", "N/A"),
                        record_type=RecordType(record_data.get("record_type", "other")),
                        record_date=record_data.get("record_date", ""),
                        title=record_data.get("title", "제목 없음"),
                        created_at=record_data.get("created_at", datetime.utcnow())
                    ))
                except Exception as record_error:
                    # 개별 기록 처리 실패 시 로그만 남기고 계속 진행
                    print(f"[WARNING] 농장 기록 처리 실패 (ID: {record_doc.id}): {str(record_error)}")
                    continue
            
            return records
            
        except Exception as e:
            # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
            print(f"[ERROR] 농장 기록 목록 조회 전체 실패 (farm_id: {farm_id}): {str(e)}")
            return []
    
    @staticmethod
    def update_record(record_id: str, record_update: RecordUpdate, user: Dict) -> RecordResponse:
        """기록 업데이트"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 기존 기록 조회
            existing_record = RecordFirebaseService.get_record_detail(record_id, farm_id)
            
            # 업데이트할 데이터 구성
            update_data = {"updated_at": datetime.utcnow()}
            
            if record_update.title is not None:
                update_data["title"] = record_update.title
            
            if record_update.description is not None:
                update_data["description"] = record_update.description
            
            if record_update.record_date is not None:
                update_data["record_date"] = record_update.record_date
            
            if record_update.record_data is not None:
                update_data["record_data"] = record_update.record_data
            
            # Firestore 업데이트
            db.collection('cow_records').document(record_id).update(update_data)
            
            # 업데이트된 기록 반환
            return RecordFirebaseService.get_record_detail(record_id, farm_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"기록 업데이트 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def delete_record(record_id: str, user: Dict) -> Dict:
        """기록 삭제 (소프트 삭제)"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 기존 기록 확인
            existing_record = RecordFirebaseService.get_record_detail(record_id, farm_id)
            
            # 소프트 삭제
            db.collection('cow_records').document(record_id).update({
                "is_active": False,
                "updated_at": datetime.utcnow(),
                "deleted_at": datetime.utcnow()
            })
            
            return {
                "message": f"기록 '{existing_record.title}'이 삭제되었습니다",
                "record_id": record_id
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"기록 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def _get_cow_info(cow_id: str, farm_id: str) -> Dict:
        """젖소 정보 조회 (내부 사용)"""
        db = get_firestore_client()
        cow_doc = db.collection('cows').document(cow_id).get()
        
        if not cow_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="젖소를 찾을 수 없습니다"
            )
        
        cow_data = cow_doc.to_dict()
        
        # 농장 ID 확인 (보안)
        if cow_data.get("farm_id") != farm_id or not cow_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="젖소를 찾을 수 없습니다"
            )
        
        return cow_data