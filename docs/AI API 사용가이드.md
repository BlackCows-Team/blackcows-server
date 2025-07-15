# 🤖 BlackCows AI 예측 API 사용 가이드

## 📋 API 엔드포인트 목록

### 🥛 착유량 예측 API
| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|----------|
| `POST` | `/ai/milk-yield/predict` | 개별 젖소 착유량 예측 | ✅ |
| `POST` | `/ai/milk-yield/batch-predict` | 다중 젖소 착유량 일괄 예측 | ✅ |

### 🔬 유방염 예측 API
| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|----------|
| `POST` | `/ai/mastitis/predict` | 개별 젖소 유방염 예측 | ✅ |
| `POST` | `/ai/mastitis/batch-predict` | 다중 젖소 유방염 일괄 예측 | ✅ |

### 🧪 체세포수 기반 유방염 예측 API
| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|----------|
| `POST` | `/ai/scc-mastitis/predict` | 개별 젖소 체세포수 기반 유방염 예측 | ✅ |
| `POST` | `/ai/scc-mastitis/batch-predict` | 다중 젖소 체세포수 기반 유방염 일괄 예측 | ✅ |

### 🔧 테스트/개발용 API
| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|----------|
| `GET` | `/ai/test/sample-predict` | 착유량 예측 샘플 테스트 | ❌ |
| `GET` | `/ai/test/sample-mastitis-predict` | 유방염 예측 샘플 테스트 | ❌ |
| `GET` | `/ai/test/sample-scc-mastitis-predict` | 체세포수 기반 유방염 예측 샘플 테스트 | ❌ |
| `GET` | `/ai/health` | AI 서버 상태 확인 | ❌ |

---

## 🥛 착유량 예측 API

### 1️⃣ 개별 젖소 착유량 예측

**요청:**
```http
POST /ai/milk-yield/predict
Authorization: Bearer {access_token}
Content-Type: application/json
```

**요청 본문:**
```json
{
  "cow_id": "cow_123",
  "milking_frequency": 2,
  "conductivity": 7.5,
  "temperature": 38.5,
  "fat_percentage": 3.8,
  "protein_percentage": 3.2,
  "concentrate_intake": 3.5,
  "milking_month": 6,
  "milking_day_of_week": 1,
  "prediction_date": "2025-01-17",
  "notes": "정기 착유량 예측"
}
```

**응답:**
```json
{
  "prediction_id": "uuid-123",
  "cow_id": "cow_123",
  "predicted_milk_yield": 25.5,
  "confidence": 85.2,
  "input_features": {
    "착유횟수": 2,
    "전도율": 7.5,
    "온도": 38.5,
    "유지방비율": 3.8,
    "유단백비율": 3.2,
    "농후사료섭취량": 3.5,
    "착유기측정월": 6,
    "착유기측정요일": 1
  },
  "model_version": "v2.0.0",
  "prediction_time": "2025-01-17T10:30:00",
  "processing_time_ms": 45.2,
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 245.67
}
```

### 2️⃣ 다중 젖소 착유량 일괄 예측

**요청:**
```http
POST /ai/milk-yield/batch-predict
Authorization: Bearer {access_token}
Content-Type: application/json
```

**요청 본문:**
```json
{
  "predictions": [
    {
      "cow_id": "cow_123",
      "milking_frequency": 2,
      "conductivity": 7.5,
      "temperature": 38.5,
      "fat_percentage": 3.8,
      "protein_percentage": 3.2,
      "concentrate_intake": 3.5,
      "milking_month": 6,
      "milking_day_of_week": 1
    },
    {
      "cow_id": "cow_456",
      "milking_frequency": 3,
      "conductivity": 8.0,
      "temperature": 38.2,
      "fat_percentage": 4.0,
      "protein_percentage": 3.5,
      "concentrate_intake": 4.0,
      "milking_month": 6,
      "milking_day_of_week": 2
    }
  ],
  "batch_name": "오전 착유량 일괄 예측"
}
```

**응답:**
```json
{
  "batch_id": "batch-uuid-123",
  "total_predictions": 2,
  "successful_predictions": 2,
  "failed_predictions": 0,
  "predictions": [
    {
      "prediction_id": "uuid-123",
      "cow_id": "cow_123",
      "predicted_milk_yield": 25.5,
      "confidence": 85.2
    },
    {
      "prediction_id": "uuid-456",
      "cow_id": "cow_456",
      "predicted_milk_yield": 28.7,
      "confidence": 92.1
    }
  ],
  "aws_batch_id": "aws-batch-uuid",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 512.34
}
```

---

## 🔬 유방염 예측 API

### 1️⃣ 개별 젖소 유방염 예측

**요청:**
```http
POST /ai/mastitis/predict
Authorization: Bearer {access_token}
Content-Type: application/json
```

**요청 본문:**
```json
{
  "cow_id": "cow_123",
  "milk_yield": 25.5,
  "conductivity": 7.8,
  "fat_percentage": 3.6,
  "protein_percentage": 3.1,
  "lactation_number": 2,
  "prediction_date": "2025-01-17",
  "notes": "정기 유방염 검사"
}
```

**응답:**
```json
{
  "prediction_id": "uuid-456",
  "cow_id": "cow_123",
  "prediction_class": 1,
  "prediction_class_label": "주의",
  "confidence": 87.3,
  "input_features": {
    "착유량": 25.5,
    "전도율": 7.8,
    "유지방비율": 3.6,
    "유단백비율": 3.1,
    "산차수": 2
  },
  "model_version": "mastitis_rf_v1",
  "prediction_time": "2025-01-17T10:30:00",
  "processing_time_ms": 42.1,
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 245.67
}
```

### 2️⃣ 다중 젖소 유방염 일괄 예측

**요청:**
```http
POST /ai/mastitis/batch-predict
Authorization: Bearer {access_token}
Content-Type: application/json
```

**요청 본문:**
```json
{
  "predictions": [
    {
      "cow_id": "cow_123",
      "milk_yield": 25.5,
      "conductivity": 7.8,
      "fat_percentage": 3.6,
      "protein_percentage": 3.1,
      "lactation_number": 2
    },
    {
      "cow_id": "cow_456",
      "milk_yield": 22.1,
      "conductivity": 8.2,
      "fat_percentage": 3.9,
      "protein_percentage": 3.4,
      "lactation_number": 1
    }
  ],
  "batch_name": "오전 유방염 일괄 검사"
}
```

**응답:**
```json
{
  "batch_id": "batch-uuid-789",
  "total_predictions": 2,
  "successful_predictions": 2,
  "failed_predictions": 0,
  "predictions": [
    {
      "prediction_id": "uuid-456",
      "cow_id": "cow_123",
      "prediction_class": 1,
      "prediction_class_label": "주의",
      "confidence": 87.3
    },
    {
      "prediction_id": "uuid-789",
      "cow_id": "cow_456",
      "prediction_class": 0,
      "prediction_class_label": "정상",
      "confidence": 91.2
    }
  ],
  "aws_batch_id": "aws-batch-uuid-2",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 434.21
}
```

---

## 🧪 체세포수 기반 유방염 예측 API

### 1️⃣ 개별 젖소 체세포수 기반 유방염 예측

**요청:**
```http
POST /ai/scc-mastitis/predict
Authorization: Bearer {access_token}
Content-Type: application/json
```

**요청 본문:**
```json
{
  "cow_id": "cow_456", 
  "somatic_cell_count": 180000,
  "prediction_date": "2025-01-17",
  "notes": "체세포수 증가로 인한 검사"
}
```

**응답:**
```json
{
  "prediction_id": "uuid-scc-123",
  "cow_id": "cow_456",
  "prediction_class": 1,
  "prediction_class_label": "주의",
  "confidence": 89.7,
  "input_features": {
    "체세포수": 180000
  },
  "model_version": "scc_mastitis_v1",
  "prediction_time": "2025-01-17T10:30:00",
  "processing_time_ms": 38.5,
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 198.43
}
```

### 2️⃣ 다중 젖소 체세포수 기반 유방염 일괄 예측

**요청:**
```http
POST /ai/scc-mastitis/batch-predict
Authorization: Bearer {access_token}
Content-Type: application/json
```

**요청 본문:**
```json
{
  "predictions": [
    {
      "cow_id": "cow_123",
      "somatic_cell_count": 120000
    },
    {
      "cow_id": "cow_456",
      "somatic_cell_count": 250000
    }
  ],
  "batch_name": "체세포수 기반 일괄 검사"
}
```

**응답:**
```json
{
  "batch_id": "scc-batch-uuid-456",
  "total_predictions": 2,
  "successful_predictions": 2,
  "failed_predictions": 0,
  "predictions": [
    {
      "prediction_id": "uuid-scc-123",
      "cow_id": "cow_123",
      "prediction_class": 0,
      "prediction_class_label": "정상",
      "confidence": 93.1
    },
    {
      "prediction_id": "uuid-scc-456",
      "cow_id": "cow_456",
      "prediction_class": 2,
      "prediction_class_label": "위험",
      "confidence": 88.9
    }
  ],
  "aws_batch_id": "aws-scc-batch-uuid",
  "user_id": "user123",
  "farm_id": "farm-uuid",
  "requested_at": "2025-01-17T10:30:00Z",
  "server_processing_time_ms": 298.76
}
```

---

## 🔧 테스트 API

### 1️⃣ 착유량 예측 샘플 테스트

**요청:**
```http
GET /ai/test/sample-predict
```

**응답:**
```json
{
  "prediction_id": "test-uuid",
  "cow_id": "test_cow",
  "predicted_milk_yield": 24.8,
  "confidence": 78.5,
  "test_status": "success",
  "message": "샘플 예측 테스트 성공"
}
```

### 2️⃣ 유방염 예측 샘플 테스트

**요청:**
```http
GET /ai/test/sample-mastitis-predict
```

**응답:**
```json
{
  "prediction_id": "test-mastitis-uuid",
  "cow_id": "test_cow",
  "prediction_class": 0,
  "prediction_class_label": "정상",
  "confidence": 82.3,
  "test_status": "success",
  "message": "샘플 유방염 예측 테스트 성공"
}
```

### 3️⃣ 체세포수 기반 유방염 예측 샘플 테스트

**요청:**
```http
GET /ai/test/sample-scc-mastitis-predict
```

**응답:**
```json
{
  "prediction_id": "test-scc-uuid",
  "cow_id": "test_cow",
  "prediction_class": 1,
  "prediction_class_label": "주의",
  "confidence": 85.7,
  "test_status": "success",
  "message": "샘플 체세포수 기반 유방염 예측 테스트 성공"
}
```

### 4️⃣ AI 서버 상태 확인

**요청:**
```http
GET /ai/health
```

**응답:**
```json
{
  "aws_server_status": "healthy",
  "ai_server_connection": "connected",
  "ai_server_url": "https://feof-implement-finnish-finally.trycloudflare.com",
  "ai_server_health": {
    "status": "healthy",
    "message": "AI 예측 서비스가 정상 작동 중입니다",
    "model_info": {
      "milk_yield_model": "available",
      "mastitis_model": "available",
      "scc_mastitis_model": "available"
    }
  },
  "timestamp": "2025-01-17T10:30:00Z",
  "service_ready": true
}
```

---

## 📱 Flutter 클라이언트 예시

### 🥛 착유량 예측
```dart
Future<Map<String, dynamic>> predictMilkYield({
  required String cowId,
  required int milkingFrequency,
  required double conductivity,
  required double temperature,
  required double fatPercentage,
  required double proteinPercentage,
  required double concentrateIntake,
  required int milkingMonth,
  required int milkingDayOfWeek,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ai/milk-yield/predict'),
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'cow_id': cowId,
      'milking_frequency': milkingFrequency,
      'conductivity': conductivity,
      'temperature': temperature,
      'fat_percentage': fatPercentage,
      'protein_percentage': proteinPercentage,
      'concentrate_intake': concentrateIntake,
      'milking_month': milkingMonth,
      'milking_day_of_week': milkingDayOfWeek,
      'prediction_date': DateTime.now().toIso8601String().split('T')[0],
    }),
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('착유량 예측 실패: ${response.body}');
  }
}
```

### 🔬 유방염 예측
```dart
Future<Map<String, dynamic>> predictMastitis({
  required String cowId,
  required double milkYield,
  required double conductivity,
  required double fatPercentage,
  required double proteinPercentage,
  required int lactationNumber,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ai/mastitis/predict'),
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'cow_id': cowId,
      'milk_yield': milkYield,
      'conductivity': conductivity,
      'fat_percentage': fatPercentage,
      'protein_percentage': proteinPercentage,
      'lactation_number': lactationNumber,
      'prediction_date': DateTime.now().toIso8601String().split('T')[0],
    }),
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('유방염 예측 실패: ${response.body}');
  }
}
```

### 🧪 체세포수 기반 유방염 예측
```dart
Future<Map<String, dynamic>> predictSCCMastitis({
  required String cowId,
  required int somaticCellCount,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ai/scc-mastitis/predict'),
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'cow_id': cowId,
      'somatic_cell_count': somaticCellCount,
      'prediction_date': DateTime.now().toIso8601String().split('T')[0],
    }),
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('체세포수 기반 유방염 예측 실패: ${response.body}');
  }
}
```

---

## ⚠️ 에러 처리

### 일반적인 에러 응답 형태
```json
{
  "detail": {
    "error_code": "AI_SERVER_UNAVAILABLE",
    "error_message": "AI 서버에 연결할 수 없습니다",
    "suggestion": "잠시 후 다시 시도하거나 관리자에게 문의하세요"
  }
}
```

### 주요 에러 코드

| 에러 코드 | 설명 | 해결 방법 |
|-----------|------|-----------|
| `AI_MODEL_UNAVAILABLE` | AI 모델을 사용할 수 없음 | 잠시 후 재시도 |
| `AI_SERVER_TIMEOUT` | AI 서버 응답 시간 초과 | 잠시 후 재시도 |
| `AI_SERVER_UNAVAILABLE` | AI 서버 연결 실패 | 관리자 문의 |
| `PREDICTION_PROCESSING_FAILED` | 예측 처리 중 오류 | 입력값 확인 후 재시도 |

---

## 📊 예측 결과 해석

### 착유량 예측 결과
- **predicted_milk_yield**: 예상 착유량 (리터)
- **confidence**: 예측 신뢰도 (0-100%)

### 유방염 예측 결과
- **prediction_class**: 
  - `0`: 정상
  - `1`: 주의 
  - `2`: 염증 가능성 + 유방염 의심
- **confidence**: 예측 신뢰도 (0-100%)

### 체세포수 기반 유방염 예측 결과
- **prediction_class**:
  - `0`: 정상 (체세포수 정상 범위)
  - `1`: 주의 (체세포수 약간 증가)
  - `2`: 위험 (체세포수 고위험 범위)
- **confidence**: 예측 신뢰도 (0-100%)

---