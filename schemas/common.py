from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime

class ApiResponse(BaseModel):
    """표준 API 응답 형식"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class PaginationResponse(BaseModel):
    """페이지네이션 응답 형식"""
    success: bool = True
    message: str = "조회 성공"
    data: List[Any]
    pagination: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

class ErrorResponse(BaseModel):
    """에러 응답 형식"""
    success: bool = False
    message: str
    error: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class ValidationErrorResponse(BaseModel):
    """유효성 검사 에러 응답 형식"""
    success: bool = False
    message: str = "입력 데이터 검증 실패"
    errors: List[Dict[str, Any]]
    timestamp: datetime = datetime.utcnow() 