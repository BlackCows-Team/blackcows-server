# 🐄 유방염 예측 AI API 사용 가이드

## 개요
- ✅ **외부 AI 서버 연동**: Cloudflare Tunnel을 통한 안정적인 AI 서버 연결
- ✅ **개별 젖소 유방염 예측**: 젖소의 5가지 특성(착유량, 전도율, 유지방비율, 유단백비율, 산차수)을 바탕으로 유방염 위험도를 예측합니다.
- ✅ **다중 젖소 유방염 일괄 예측**: 여러 젖소의 유방염 위험도를 한 번에 예측하여 효율적인 관리를 돕습니다.
- ✅ **체세포수 기반 유방염 예측**: 젖소의 체세포수만으로 유방염 위험도를 예측합니다.
- ✅ **실시간 헬스체크**: AI 서버 상태 자동 모니터링 및 오류 처리
- ✅ **메타데이터 보강**: 사용자 정보, 농장 정보, 처리 시간 등 추가 정보 제공

---

## 유방염 예측 API

| Method | Endpoint | 설명 | 필수 필드 | 응답 |
|--------|----------|------|----------|------|
| `POST` | `/ai/mastitis/predict` | **개별 젖소 유방염 예측** | 착유량, 전도율, 유지방비율, 유단백비율, 산차수 | 예측 결과, 신뢰도 등 |
| `POST` | `/ai/mastitis/batch-predict` | **다중 젖소 유방염 일괄 예측** | 예측 요청 목록 | 일괄 예측 결과 |
| `POST` | `/ai/scc-mastitis/predict` | **개별 젖소 체세포수 기반 유방염 예측** | 체세포수 | 예측 결과, 신뢰도 등 |
| `POST` | `/ai/scc-mastitis/batch-predict` | **다중 젖소 체세포수 기반 유방염 일괄 예측** | 예측 요청 목록 | 일괄 예측 결과 |

---

### 1. 유방염 예측 요청 예시

```json
POST /ai/mastitis/predict
{
  "cow_id": "cow-uuid-123",           // 선택사항
  "milk_yield": 25.5,                 // 필수: 착유량 (리터)
  "conductivity": 7.7,                // 필수: 전도율
  "fat_percentage": 3.8,              // 필수: 유지방비율 (%)
  "protein_percentage": 3.2,          // 필수: 유단백비율 (%)
  "lactation_number": 2,              // 필수: 산차수
  "prediction_date": "2025-01-17",    // 선택사항: 예측 기준일
  "notes": "정기 유방염 예측"         // 선택사항: 예측 관련 메모
}
```

#### 유방염 예측 응답 예시

```json
{
  "prediction_class": "염증 가능성",      // 예측 클래스: 정상, 주의, 염증 가능성
  "confidence_score": 0.87,              // 신뢰도 점수 (0~1)
  "model_version": "v2.0.0",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 210.45
}
```

---

### 2. 다중 젖소 유방염 예측 요청 예시

```json
POST /ai/mastitis/batch-predict
{
  "predictions": [
    {
      "cow_id": "cow-uuid-123",
      "milk_yield": 25.5,
      "conductivity": 7.7,
      "fat_percentage": 3.8,
      "protein_percentage": 3.2,
      "lactation_number": 2
    },
    {
      "cow_id": "cow-uuid-456",
      "milk_yield": 28.1,
      "conductivity": 8.1,
      "fat_percentage": 4.1,
      "protein_percentage": 3.4,
      "lactation_number": 3
    }
  ],
  "batch_name": "오전 유방염 예측"
}
```

#### 다중 젖소 유방염 예측 응답 예시

```json
{
  "batch_id": "batch-uuid-123",
  "successful_predictions": 2,
  "failed_predictions": 0,
  "predictions": [
    {
      "cow_id": "cow-uuid-123",
      "prediction_class": "정상",
      "confidence_score": 0.91
    },
    {
      "cow_id": "cow-uuid-456",
      "prediction_class": "염증 가능성",
      "confidence_score": 0.85
    }
  ],
  "aws_batch_id": "aws-batch-uuid",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 430.12
}
```

---

### 3. 체세포수 기반 유방염 예측 요청 예시

```json
POST /ai/scc-mastitis/predict
{
  "cow_id": "cow-uuid-123",           // 선택사항
  "somatic_cell_count": 145,           // 필수: 체세포수
  "prediction_date": "2025-01-17",    // 선택사항: 예측 기준일
  "notes": "정기 체세포수 예측"         // 선택사항: 예측 관련 메모
}
```

#### 체세포수 기반 유방염 예측 응답 예시

```json
{
  "prediction_class": "위험",           // 예측 클래스: 정상, 주의, 위험
  "confidence_score": 0.93,            // 신뢰도 점수 (0~1)
  "model_version": "v2.0.0",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 180.22
}
```

---

### 4. 다중 젖소 체세포수 기반 유방염 예측 요청 예시

```json
POST /ai/scc-mastitis/batch-predict
{
  "predictions": [
    {
      "cow_id": "cow-uuid-123",
      "somatic_cell_count": 145
    },
    {
      "cow_id": "cow-uuid-456",
      "somatic_cell_count": 320
    }
  ],
  "batch_name": "오전 체세포수 예측"
}
```

#### 다중 젖소 체세포수 기반 유방염 예측 응답 예시

```json
{
  "batch_id": "batch-uuid-456",
  "successful_predictions": 2,
  "failed_predictions": 0,
  "predictions": [
    {
      "cow_id": "cow-uuid-123",
      "prediction_class": "정상",
      "confidence_score": 0.95
    },
    {
      "cow_id": "cow-uuid-456",
      "prediction_class": "위험",
      "confidence_score": 0.88
    }
  ],
  "aws_batch_id": "aws-batch-uuid",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 390.11
}
```

---

> 문의 및 추가 요청 사항은 개발팀에 연락해 주세요. 