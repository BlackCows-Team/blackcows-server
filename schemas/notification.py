# schemas/notification.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# 알림 유형
class NotificationType(str, Enum):
    # ===== 할일 관련 알림 =====
    TASK_DUE_SOON = "task_due_soon"           # 할일 마감 임박 (1시간 전)
    TASK_OVERDUE = "task_overdue"             # 할일 지연
    TASK_COMPLETED = "task_completed"         # 할일 완료
    TASK_CREATED = "task_created"             # 할일 생성
    TASK_ASSIGNED = "task_assigned"           # 할일 배정
    
    # ===== 젖소 기본 관리 관련 =====
    COW_REGISTERED = "cow_registered"         # 젖소 등록 완료
    COW_UPDATED = "cow_updated"               # 젖소 정보 수정
    COW_DELETED = "cow_deleted"               # 젖소 삭제
    COW_FAVORITE_ADDED = "cow_favorite_added" # 젖소 즐겨찾기 추가
    COW_FAVORITE_REMOVED = "cow_favorite_removed" # 젖소 즐겨찾기 제거
    
    # ===== 축산물이력제 연동 관련 =====
    LIVESTOCK_TRACE_SUCCESS = "livestock_trace_success" # 축산물이력제 조회 성공
    LIVESTOCK_TRACE_FAILED = "livestock_trace_failed"   # 축산물이력제 조회 실패
    LIVESTOCK_TRACE_ALREADY_REGISTERED = "livestock_trace_already_registered" # 이미 등록된 젖소
    
    # ===== 착유 관련 알림 =====
    MILKING_RECORD_CREATED = "milking_record_created"   # 착유 기록 생성
    MILKING_YIELD_LOW = "milking_yield_low"             # 착유량 저하 (정상 대비 20% 이상 감소)
    MILKING_YIELD_HIGH = "milking_yield_high"           # 착유량 증가 (정상 대비 20% 이상 증가)
    MILKING_MISSED = "milking_missed"                   # 착유 누락 (예정된 착유 시간 지남)
    MILKING_QUALITY_ISSUE = "milking_quality_issue"     # 착유 품질 문제 (체세포수 높음, 혈액 감지 등)
    MILKING_SCHEDULE_REMINDER = "milking_schedule_reminder" # 착유 일정 알림
    
    # ===== 번식 관리 관련 알림 =====
    ESTRUS_DETECTED = "estrus_detected"                 # 발정 감지
    ESTRUS_PREDICTED = "estrus_predicted"               # 발정 예측 (다음 발정 예상일)
    INSEMINATION_SCHEDULED = "insemination_scheduled"   # 인공수정 예정
    INSEMINATION_COMPLETED = "insemination_completed"   # 인공수정 완료
    PREGNANCY_CHECK_DUE = "pregnancy_check_due"         # 임신감정 예정일
    PREGNANCY_CONFIRMED = "pregnancy_confirmed"         # 임신 확인
    PREGNANCY_FAILED = "pregnancy_failed"               # 임신 실패
    CALVING_PREDICTED = "calving_predicted"             # 분만 예정일 (임신 280일)
    CALVING_IMMINENT = "calving_imminent"               # 분만 임박 (분만 예정일 1주일 전)
    CALVING_COMPLETED = "calving_completed"             # 분만 완료
    CALVING_DIFFICULTY = "calving_difficulty"           # 분만 어려움
    ABORTION_DETECTED = "abortion_detected"             # 유산 감지
    DRY_OFF_SCHEDULED = "dry_off_scheduled"             # 건유 전환 예정
    DRY_OFF_COMPLETED = "dry_off_completed"             # 건유 전환 완료
    
    # ===== 건강 관리 관련 알림 =====
    HEALTH_CHECK_DUE = "health_check_due"               # 건강검진 예정
    HEALTH_CHECK_COMPLETED = "health_check_completed"   # 건강검진 완료
    HEALTH_ISSUE_DETECTED = "health_issue_detected"     # 건강 문제 감지
    VACCINATION_DUE = "vaccination_due"                 # 백신 접종 예정
    VACCINATION_COMPLETED = "vaccination_completed"     # 백신 접종 완료
    VACCINATION_OVERDUE = "vaccination_overdue"         # 백신 접종 지연
    TREATMENT_STARTED = "treatment_started"             # 치료 시작
    TREATMENT_COMPLETED = "treatment_completed"         # 치료 완료
    TREATMENT_FOLLOW_UP = "treatment_follow_up"         # 치료 후속 관찰
    DISEASE_DETECTED = "disease_detected"               # 질병 감지
    DISEASE_RECOVERY = "disease_recovery"               # 질병 회복
    
    # ===== 사료 관리 관련 알림 =====
    FEED_SCHEDULE_REMINDER = "feed_schedule_reminder"   # 사료 급여 일정 알림
    FEED_RECORD_CREATED = "feed_record_created"         # 사료 급여 기록 생성
    FEED_QUALITY_ISSUE = "feed_quality_issue"           # 사료 품질 문제
    FEED_SHORTAGE = "feed_shortage"                     # 사료 부족
    FEED_ORDER_DUE = "feed_order_due"                   # 사료 주문 예정
    
    # ===== 체중 관리 관련 알림 =====
    WEIGHT_MEASUREMENT_DUE = "weight_measurement_due"   # 체중 측정 예정
    WEIGHT_ABNORMAL = "weight_abnormal"                 # 체중 이상 (급격한 증감)
    WEIGHT_TARGET_REACHED = "weight_target_reached"     # 목표 체중 달성
    
    # ===== 검사 관련 알림 =====
    BRUCELLA_TEST_DUE = "brucella_test_due"             # 브루셀라 검사 예정
    BRUCELLA_TEST_RESULT = "brucella_test_result"       # 브루셀라 검사 결과
    TUBERCULOSIS_TEST_DUE = "tuberculosis_test_due"     # 결핵 검사 예정
    TUBERCULOSIS_TEST_RESULT = "tuberculosis_test_result" # 결핵 검사 결과
    
    # ===== 시스템 및 관리 관련 알림 =====
    SYSTEM_MAINTENANCE = "system_maintenance"           # 시스템 점검
    SECURITY_ALERT = "security_alert"                   # 보안 알림
    WELCOME = "welcome"                                 # 환영 알림
    ACCOUNT_CREATED = "account_created"                 # 계정 생성
    ACCOUNT_UPDATED = "account_updated"                 # 계정 정보 수정
    PASSWORD_CHANGED = "password_changed"               # 비밀번호 변경
    LOGIN_ATTEMPT = "login_attempt"                     # 로그인 시도
    LOGIN_FAILED = "login_failed"                       # 로그인 실패
    LOGIN_SUCCESS = "login_success"                     # 로그인 성공
    
    # ===== 통계 및 분석 관련 알림 =====
    DAILY_SUMMARY = "daily_summary"                     # 일일 요약
    WEEKLY_SUMMARY = "weekly_summary"                   # 주간 요약
    MONTHLY_SUMMARY = "monthly_summary"                 # 월간 요약
    PERFORMANCE_ALERT = "performance_alert"             # 성과 알림 (착유량, 번식율 등)
    TREND_ANALYSIS = "trend_analysis"                   # 트렌드 분석 결과
    
    # ===== AI 챗봇 관련 알림 =====
    CHATBOT_QUESTION_ANSWERED = "chatbot_question_answered" # 챗봇 질문 답변 완료
    CHATBOT_SUGGESTION = "chatbot_suggestion"           # 챗봇 제안사항
    
    # ===== 기록 관리 관련 알림 =====
    RECORD_CREATED = "record_created"                   # 기록 생성
    RECORD_UPDATED = "record_updated"                   # 기록 수정
    RECORD_DELETED = "record_deleted"                   # 기록 삭제
    RECORD_MISSING = "record_missing"                   # 기록 누락 (예정된 기록 미입력)
    
    # ===== 특수 상황 관련 알림 =====
    EMERGENCY_ALERT = "emergency_alert"                 # 긴급 상황
    WEATHER_ALERT = "weather_alert"                     # 날씨 알림 (폭우, 폭설 등)
    EQUIPMENT_FAILURE = "equipment_failure"             # 장비 고장
    SUPPLY_SHORTAGE = "supply_shortage"                 # 물품 부족
    VETERINARIAN_VISIT = "veterinarian_visit"           # 수의사 방문 예정
    INSPECTION_DUE = "inspection_due"                   # 검사 예정 (정부, 협회 등)
    
    # ===== 알림 설정 관련 =====
    NOTIFICATION_SETTINGS_UPDATED = "notification_settings_updated" # 알림 설정 변경
    NOTIFICATION_TEST = "notification_test"             # 알림 테스트

# 알림 채널
class NotificationChannel(str, Enum):
    IN_APP = "in_app"           # 앱 내 알림
    EMAIL = "email"             # 이메일 알림
    PUSH = "push"               # 푸시 알림 (향후)
    SMS = "sms"                 # SMS 알림 (향후)

# 알림 우선순위
class NotificationPriority(str, Enum):
    LOW = "low"         # 낮음
    MEDIUM = "medium"   # 보통
    HIGH = "high"       # 높음
    URGENT = "urgent"   # 긴급

# 알림 상태
class NotificationStatus(str, Enum):
    UNREAD = "unread"   # 읽지 않음
    READ = "read"       # 읽음
    ARCHIVED = "archived" # 보관됨

# 알림 생성 스키마
class NotificationCreate(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    notification_type: NotificationType = Field(..., description="알림 유형")
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 메시지")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM, description="우선순위")
    data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")
    related_cow_id: Optional[str] = Field(None, description="관련 젖소 ID")
    related_task_id: Optional[str] = Field(None, description="관련 할일 ID")
    related_record_id: Optional[str] = Field(None, description="관련 기록 ID")
    scheduled_at: Optional[datetime] = Field(None, description="예약 발송 시간")
    expires_at: Optional[datetime] = Field(None, description="만료 시간")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('알림 제목은 필수입니다')
        if len(v) > 200:
            raise ValueError('알림 제목은 200자 이하여야 합니다')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('알림 메시지는 필수입니다')
        if len(v) > 1000:
            raise ValueError('알림 메시지는 1000자 이하여야 합니다')
        return v.strip()

# 알림 응답 스키마
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    status: NotificationStatus
    data: Optional[Dict[str, Any]]
    related_cow_id: Optional[str]
    related_cow_name: Optional[str]
    related_task_id: Optional[str]
    related_record_id: Optional[str]
    created_at: datetime
    read_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool

# 알림 요약 스키마 (목록용)
class NotificationSummary(BaseModel):
    id: str
    notification_type: NotificationType
    title: str
    priority: NotificationPriority
    status: NotificationStatus
    related_cow_name: Optional[str]
    created_at: datetime
    is_overdue: bool

# 알림 업데이트 스키마
class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None

# 알림 설정 스키마
class NotificationSettings(BaseModel):
    user_id: str
    # 할일 관련 설정
    task_due_soon: bool = True
    task_overdue: bool = True
    task_completed: bool = True
    
    # 젖소 관리 관련 설정
    cow_registered: bool = True
    cow_updated: bool = True
    cow_deleted: bool = True
    
    # 착유 관련 설정
    milking_record_created: bool = True
    milking_yield_alert: bool = True
    milking_missed: bool = True
    milking_quality_issue: bool = True
    
    # 번식 관련 설정
    estrus_detected: bool = True
    insemination_scheduled: bool = True
    pregnancy_check_due: bool = True
    calving_predicted: bool = True
    calving_imminent: bool = True
    
    # 건강 관리 관련 설정
    health_check_due: bool = True
    vaccination_due: bool = True
    treatment_started: bool = True
    disease_detected: bool = True
    
    # 사료 관리 관련 설정
    feed_schedule_reminder: bool = True
    feed_quality_issue: bool = True
    feed_shortage: bool = True
    
    # 체중 관리 관련 설정
    weight_measurement_due: bool = True
    weight_abnormal: bool = True
    
    # 검사 관련 설정
    brucella_test_due: bool = True
    tuberculosis_test_due: bool = True
    
    # 시스템 관련 설정
    system_maintenance: bool = True
    security_alert: bool = True
    emergency_alert: bool = True
    
    # 통계 관련 설정
    daily_summary: bool = True
    weekly_summary: bool = True
    monthly_summary: bool = True
    
    # 알림 방법 설정
    push_notification: bool = True
    email_notification: bool = False
    sms_notification: bool = False
    
    # 알림 시간 설정
    quiet_hours_start: Optional[str] = None  # HH:MM 형식
    quiet_hours_end: Optional[str] = None    # HH:MM 형식
    
    updated_at: datetime

# 알림 통계 스키마
class NotificationStatistics(BaseModel):
    total_notifications: int
    unread_notifications: int
    read_notifications: int
    today_notifications: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    by_status: Dict[str, int]

# 알림 설정 업데이트 스키마
class NotificationSettingsUpdate(BaseModel):
    # 할일 관련 설정
    task_due_soon: Optional[bool] = None
    task_overdue: Optional[bool] = None
    task_completed: Optional[bool] = None
    
    # 젖소 관리 관련 설정
    cow_registered: Optional[bool] = None
    cow_updated: Optional[bool] = None
    cow_deleted: Optional[bool] = None
    
    # 착유 관련 설정
    milking_record_created: Optional[bool] = None
    milking_yield_alert: Optional[bool] = None
    milking_missed: Optional[bool] = None
    milking_quality_issue: Optional[bool] = None
    
    # 번식 관련 설정
    estrus_detected: Optional[bool] = None
    insemination_scheduled: Optional[bool] = None
    pregnancy_check_due: Optional[bool] = None
    calving_predicted: Optional[bool] = None
    calving_imminent: Optional[bool] = None
    
    # 건강 관리 관련 설정
    health_check_due: Optional[bool] = None
    vaccination_due: Optional[bool] = None
    treatment_started: Optional[bool] = None
    disease_detected: Optional[bool] = None
    
    # 사료 관리 관련 설정
    feed_schedule_reminder: Optional[bool] = None
    feed_quality_issue: Optional[bool] = None
    feed_shortage: Optional[bool] = None
    
    # 체중 관리 관련 설정
    weight_measurement_due: Optional[bool] = None
    weight_abnormal: Optional[bool] = None
    
    # 검사 관련 설정
    brucella_test_due: Optional[bool] = None
    tuberculosis_test_due: Optional[bool] = None
    
    # 시스템 관련 설정
    system_maintenance: Optional[bool] = None
    security_alert: Optional[bool] = None
    emergency_alert: Optional[bool] = None
    
    # 통계 관련 설정
    daily_summary: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    monthly_summary: Optional[bool] = None
    
    # 알림 방법 설정
    push_notification: Optional[bool] = None
    email_notification: Optional[bool] = None
    sms_notification: Optional[bool] = None
    
    # 알림 시간 설정
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

# 알림 일괄 처리 스키마
class NotificationBatchRequest(BaseModel):
    user_ids: List[str] = Field(..., description="수신자 사용자 ID 목록")
    farm_id: str = Field(..., description="농장 ID")
    notification_type: NotificationType = Field(..., description="알림 유형")
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 내용")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM, description="우선순위")
    channels: List[NotificationChannel] = Field([NotificationChannel.IN_APP], description="발송 채널")
    
    # 관련 데이터
    related_task_id: Optional[str] = Field(None, description="관련 할일 ID")
    related_cow_id: Optional[str] = Field(None, description="관련 젖소 ID")
    related_record_id: Optional[str] = Field(None, description="관련 기록 ID")
    
    # 스케줄링
    scheduled_at: Optional[datetime] = Field(None, description="예약 발송 시간")
    metadata: Optional[Dict[str, Any]] = Field(None, description="추가 메타데이터") 