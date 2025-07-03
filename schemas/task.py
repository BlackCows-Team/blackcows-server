# schemas/task.py

from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# 할일 유형
class TaskType(str, Enum):
    PERSONAL = "personal"           # 개인 할일
    COW_SPECIFIC = "cow_specific"   # 젖소별 할일
    FARM_WIDE = "farm_wide"         # 농장 전체 할일

# 우선순위
class TaskPriority(str, Enum):
    LOW = "low"         # 낮음
    MEDIUM = "medium"   # 보통  
    HIGH = "high"       # 높음
    URGENT = "urgent"   # 긴급

# 카테고리
class TaskCategory(str, Enum):
    MILKING = "milking"         # 착유
    TREATMENT = "treatment"     # 치료
    VACCINATION = "vaccination" # 백신
    HEALTH_CHECK = "health_check" # 검진
    BREEDING = "breeding"       # 번식
    FEEDING = "feeding"         # 사료
    MAINTENANCE = "maintenance" # 시설 관리
    GENERAL = "general"         # 일반
    OTHER = "other"            # 기타

# 반복 주기
class TaskRecurrence(str, Enum):
    NONE = "none"       # 일회성
    DAILY = "daily"     # 매일
    WEEKLY = "weekly"   # 매주
    MONTHLY = "monthly" # 매월
    YEARLY = "yearly"   # 매년

# 할일 상태
class TaskStatus(str, Enum):
    PENDING = "pending"     # 대기중
    IN_PROGRESS = "in_progress" # 진행중
    COMPLETED = "completed" # 완료
    CANCELLED = "cancelled" # 취소
    OVERDUE = "overdue"     # 지연

# 할일 생성 스키마
class TaskCreate(BaseModel):
    title: str = Field(..., description="할일 제목")
    description: Optional[str] = Field(None, description="할일 설명")
    task_type: TaskType = Field(..., description="할일 유형")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="우선순위")
    due_date: Optional[str] = Field(None, description="마감일 (YYYY-MM-DD)")
    due_time: Optional[str] = Field(None, description="마감 시간 (HH:MM)")
    category: TaskCategory = Field(TaskCategory.GENERAL, description="카테고리")
    related_cow_id: Optional[str] = Field(None, description="관련 젖소 ID")
    auto_generated: bool = Field(False, description="자동 생성 여부")
    recurrence: TaskRecurrence = Field(TaskRecurrence.NONE, description="반복 주기")
    notes: Optional[str] = Field(None, description="추가 메모")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('할일 제목은 필수입니다')
        if len(v) > 200:
            raise ValueError('할일 제목은 200자 이하여야 합니다')
        return v.strip()
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('마감일은 YYYY-MM-DD 형식으로 입력해주세요')
        return v
    
    @validator('due_time')
    def validate_due_time(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                datetime.strptime(v.strip(), '%H:%M')
                return v.strip()
            except ValueError:
                raise ValueError('마감 시간은 HH:MM 형식으로 입력해주세요')
        return v

# 할일 업데이트 스키마
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    category: Optional[TaskCategory] = None
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('할일 제목은 비어있을 수 없습니다')
            if len(v) > 200:
                raise ValueError('할일 제목은 200자 이하여야 합니다')
            return v.strip()
        return v

# 할일 응답 스키마
class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[str]
    due_time: Optional[str]
    category: TaskCategory
    related_cow_id: Optional[str]
    related_cow_name: Optional[str]
    related_cow_ear_tag: Optional[str]
    auto_generated: bool
    recurrence: TaskRecurrence
    notes: Optional[str]
    farm_id: str
    owner_id: str
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 할일 요약 스키마 (목록용)
class TaskSummary(BaseModel):
    id: str
    title: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[str]
    due_time: Optional[str]
    category: TaskCategory
    related_cow_name: Optional[str]
    is_overdue: bool
    created_at: datetime

# 할일 완료 스키마
class TaskComplete(BaseModel):
    completion_notes: Optional[str] = Field(None, description="완료 메모")
    
# 할일 통계 스키마
class TaskStatistics(BaseModel):
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    overdue_tasks: int
    today_tasks: int
    high_priority_tasks: int
    by_category: dict
    by_priority: dict
    completion_rate: float

# 캘린더 뷰용 할일 아이템 스키마
class CalendarTaskItem(BaseModel):
    id: str
    title: str
    status: TaskStatus
    category: TaskCategory
    priority: TaskPriority
    due_time: Optional[str]

# 캘린더 뷰 응답 스키마
class CalendarResponse(BaseModel):
    dates: dict  # "YYYY-MM-DD": List[CalendarTaskItem]