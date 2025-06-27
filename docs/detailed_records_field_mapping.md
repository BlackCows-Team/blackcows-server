# 🐄 젖소 상세기록 필드 매핑 문서

## 📋 개요

이 문서는 BlackCows 젖소 관리 시스템의 모든 상세기록 유형과 각 필드가 Firebase Firestore의 어느 위치에 저장되는지 정리한 문서입니다. 

### 🗄️ Firebase 컬렉션 구조

```
cow_detailed_records/
├── {record_id}/
│   ├── id: string                  # 기록 고유 ID
│   ├── cow_id: string              # 젖소 ID
│   ├── record_type: string         # 기록 유형
│   ├── record_date: string         # 기록 날짜 (YYYY-MM-DD)
│   ├── title: string               # 기록 제목
│   ├── description: string         # 기록 설명
│   ├── record_data: object         # 실제 기록 데이터 (유형별 상이)
│   ├── farm_id: string             # 농장 ID
│   ├── owner_id: string            # 소유자 ID
│   ├── created_at: timestamp       # 생성일시
│   ├── updated_at: timestamp       # 수정일시
│   └── is_active: boolean          # 활성 상태
```

---

## 📊 상세기록 유형별 필드 매핑

### 1. 🥛 착유 기록 (milking)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 착유한 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 착유량 | 착유량 | `milk_yield` | float | ✅ | 리터(L) 단위, 0보다 커야 함 |
| 착유 시작 시간 | 착유 시작 시간 | `milking_start_time` | string | ❌ | HH:MM:SS 형식 |
| 착유 종료 시간 | 착유 종료 시간 | `milking_end_time` | string | ❌ | HH:MM:SS 형식 |
| 착유 횟수 | 착유 회차 | `milking_session` | integer | ❌ | 1회차, 2회차 등 |
| 전도율 | 우유 전도율 | `conductivity` | float | ❌ | 전기 전도율 수치 |
| 체세포수 | 체세포 수 | `somatic_cell_count` | integer | ❌ | 0-10,000,000 범위 |
| 혈액 흐름 감지 | 혈액 흐름 감지 여부 | `blood_flow_detected` | boolean | ❌ | true/false |
| 색상값 | 우유 색상 | `color_value` | string | ❌ | 색상 상태 |
| 온도 | 우유 온도 | `temperature` | float | ❌ | 섭씨(°C) 단위 |
| 유지방 비율 | 유지방 함량 | `fat_percentage` | float | ❌ | 백분율(%) |
| 유단백 비율 | 유단백 함량 | `protein_percentage` | float | ❌ | 백분율(%) |
| 공기 흐름값 | 공기 흐름 수치 | `air_flow_value` | float | ❌ | 공기 흐름 측정값 |
| 산차수 | 출산 횟수 | `lactation_number` | integer | ❌ | 몇 번째 비유기인지 |
| 반추 시간 | 반추 시간 | `rumination_time` | integer | ❌ | 분 단위 |
| 수집 구분 코드 | 수집 방법 코드 | `collection_code` | string | ❌ | AUTO, MANUAL 등 |
| 수집 건수 | 수집 횟수 | `collection_count` | integer | ❌ | 수집 건수 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 2. 💕 발정 기록 (estrus)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 발정 발견 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 발정 시작 시간 | 발정 시작 시간 | `estrus_start_time` | string | ❌ | HH:MM:SS 형식 |
| 발정 강도 | 발정 강도 | `estrus_intensity` | string | ❌ | 약/중/강 |
| 발정 지속시간 | 발정 지속 시간 | `estrus_duration` | integer | ❌ | 시간 단위 |
| 행동 징후 | 발정 행동 징후 | `behavior_signs` | array | ❌ | 문자열 배열 |
| 육안 관찰 사항 | 육안 관찰 징후 | `visual_signs` | array | ❌ | 문자열 배열 |
| 발견자 | 발정 발견자 | `detected_by` | string | ❌ | 발견한 사람 이름 |
| 발견 방법 | 발견 방법 | `detection_method` | string | ❌ | 육안/센서/기타 |
| 다음 발정 예상일 | 다음 발정 예상일 | `next_expected_estrus` | string | ❌ | YYYY-MM-DD 형식 |
| 교배 계획 여부 | 교배 계획 | `breeding_planned` | boolean | ❌ | true/false |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 3. 🎯 인공수정 기록 (insemination)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 인공수정 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 수정 시간 | 인공수정 시간 | `insemination_time` | string | ❌ | HH:MM:SS 형식 |
| 종축 ID | 종축 식별자 | `bull_id` | string | ❌ | 종축 고유 번호 |
| 종축 품종 | 종축 품종 | `bull_breed` | string | ❌ | 홀스타인 등 |
| 정액 로트번호 | 정액 배치 번호 | `semen_batch` | string | ❌ | 정액 로트 정보 |
| 정액 품질등급 | 정액 품질 | `semen_quality` | string | ❌ | 등급 정보 |
| 수정사 이름 | 수정사 | `technician_name` | string | ❌ | 수정 담당자 |
| 수정 방법 | 수정 방법 | `insemination_method` | string | ❌ | 수정 기법 |
| 자궁경관 상태 | 자궁경관 상태 | `cervix_condition` | string | ❌ | 자궁경관 조건 |
| 성공 예상률 | 성공 확률 | `success_probability` | float | ❌ | 백분율(%) |
| 비용 | 수정 비용 | `cost` | float | ❌ | 원 단위 |
| 임신감정 예정일 | 임신감정 예정일 | `pregnancy_check_scheduled` | string | ❌ | YYYY-MM-DD 형식 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 4. 🤱 임신감정 기록 (pregnancy_check)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 임신감정 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 감정 방법 | 임신감정 방법 | `check_method` | string | ❌ | 직장검사/초음파/혈액검사 |
| 감정 결과 | 임신감정 결과 | `check_result` | string | ❌ | 임신/비임신/의심 |
| 임신 단계 | 임신 일수 | `pregnancy_stage` | integer | ❌ | 임신 일수 |
| 태아 상태 | 태아 상태 | `fetus_condition` | string | ❌ | 태아 건강 상태 |
| 분만예정일 | 분만 예정일 | `expected_calving_date` | string | ❌ | YYYY-MM-DD 형식 |
| 수의사명 | 수의사 | `veterinarian` | string | ❌ | 담당 수의사 |
| 감정비용 | 감정 비용 | `check_cost` | float | ❌ | 원 단위 |
| 다음 감정일 | 다음 감정일 | `next_check_date` | string | ❌ | YYYY-MM-DD 형식 |
| 추가 관리사항 | 추가 관리 | `additional_care` | string | ❌ | 특별 관리 사항 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 5. 👶 분만 기록 (calving)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 분만 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 분만 시작시간 | 분만 시작 시간 | `calving_start_time` | string | ❌ | HH:MM:SS 형식 |
| 분만 완료시간 | 분만 완료 시간 | `calving_end_time` | string | ❌ | HH:MM:SS 형식 |
| 분만 난이도 | 분만 난이도 | `calving_difficulty` | string | ❌ | 정상/약간어려움/어려움/제왕절개 |
| 송아지 수 | 송아지 마리 수 | `calf_count` | integer | ❌ | 송아지 개체 수 |
| 송아지 성별 | 송아지 성별 | `calf_gender` | array | ❌ | 문자열 배열 |
| 송아지 체중 | 송아지 체중 | `calf_weight` | array | ❌ | 숫자 배열 (kg) |
| 송아지 건강상태 | 송아지 건강 | `calf_health` | array | ❌ | 문자열 배열 |
| 태반 배출 여부 | 태반 배출 | `placenta_expelled` | boolean | ❌ | true/false |
| 태반 배출 시간 | 태반 배출 시간 | `placenta_expulsion_time` | string | ❌ | HH:MM:SS 형식 |
| 합병증 | 합병증 목록 | `complications` | array | ❌ | 문자열 배열 |
| 도움 필요 여부 | 분만 도움 | `assistance_required` | boolean | ❌ | true/false |
| 수의사 호출 여부 | 수의사 호출 | `veterinarian_called` | boolean | ❌ | true/false |
| 어미소 상태 | 어미소 상태 | `dam_condition` | string | ❌ | 어미소 건강 상태 |
| 비유 시작일 | 비유 시작일 | `lactation_start` | string | ❌ | YYYY-MM-DD 형식 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 6. 🌾 사료급여 기록 (feed)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 사료급여 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 급여 시간 | 사료급여 시간 | `feed_time` | string | ❌ | HH:MM:SS 형식 |
| 사료 종류 | 사료 유형 | `feed_type` | string | ❌ | 사료 종류명 |
| 급여량 | 사료 급여량 | `feed_amount` | float | ❌ | 킬로그램(kg) 단위 |
| 사료 품질 | 사료 품질 | `feed_quality` | string | ❌ | 품질 등급 |
| 첨가제 종류 | 첨가제 유형 | `supplement_type` | string | ❌ | 첨가제명 |
| 첨가제 양 | 첨가제 양 | `supplement_amount` | float | ❌ | 첨가제 양 |
| 음수량 | 물 섭취량 | `water_consumption` | float | ❌ | 리터(L) 단위 |
| 식욕 상태 | 식욕 상태 | `appetite_condition` | string | ❌ | 좋음/보통/나쁨 |
| 사료효율 | 사료 효율성 | `feed_efficiency` | float | ❌ | 효율 지수 |
| 사료비용 | 사료 비용 | `cost_per_feed` | float | ❌ | 원 단위 |
| 급여자 | 급여 담당자 | `fed_by` | string | ❌ | 담당자 이름 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 7. 🏥 건강검진 기록 (health_check)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 건강검진 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 검진 시간 | 건강검진 시간 | `check_time` | string | ❌ | HH:MM:SS 형식 |
| 체온 | 체온 | `body_temperature` | float | ❌ | 섭씨(°C) 단위 |
| 심박수 | 심박수 | `heart_rate` | integer | ❌ | 회/분 |
| 호흡수 | 호흡수 | `respiratory_rate` | integer | ❌ | 회/분 |
| 체형점수 | 체형점수 | `body_condition_score` | float | ❌ | 1-5 점수 |
| 유방 상태 | 유방 상태 | `udder_condition` | string | ❌ | 유방 건강 상태 |
| 발굽 상태 | 발굽 상태 | `hoof_condition` | string | ❌ | 발굽 건강 상태 |
| 털 상태 | 털 상태 | `coat_condition` | string | ❌ | 털 상태 |
| 눈 상태 | 눈 상태 | `eye_condition` | string | ❌ | 눈 건강 상태 |
| 코 상태 | 코 상태 | `nose_condition` | string | ❌ | 코 건강 상태 |
| 식욕 상태 | 식욕 | `appetite` | string | ❌ | 식욕 상태 |
| 활동성 | 활동 수준 | `activity_level` | string | ❌ | 활동성 평가 |
| 이상 증상 | 이상 증상 | `abnormal_symptoms` | array | ❌ | 문자열 배열 |
| 검진자 | 검진자 | `examiner` | string | ❌ | 검진 담당자 |
| 다음 검진일 | 다음 검진일 | `next_check_date` | string | ❌ | YYYY-MM-DD 형식 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 8. 💉 백신접종 기록 (vaccination)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 백신접종 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 접종 시간 | 백신접종 시간 | `vaccination_time` | string | ❌ | HH:MM:SS 형식 |
| 백신명 | 백신 이름 | `vaccine_name` | string | ❌ | 백신 제품명 |
| 백신 종류 | 백신 유형 | `vaccine_type` | string | ❌ | 백신 분류 |
| 백신 로트번호 | 백신 배치번호 | `vaccine_batch` | string | ❌ | 로트 정보 |
| 접종량 | 접종 용량 | `dosage` | float | ❌ | 밀리리터(ml) 단위 |
| 접종 부위 | 접종 위치 | `injection_site` | string | ❌ | 접종 부위 |
| 접종 방법 | 접종 방법 | `injection_method` | string | ❌ | 근육주사/피하주사 등 |
| 접종자 | 접종 담당자 | `administrator` | string | ❌ | 접종자 이름 |
| 제조사 | 백신 제조사 | `vaccine_manufacturer` | string | ❌ | 제조 회사 |
| 유효기간 | 백신 유효기간 | `expiry_date` | string | ❌ | YYYY-MM-DD 형식 |
| 부작용 여부 | 부작용 발생 | `adverse_reaction` | boolean | ❌ | true/false |
| 부작용 세부사항 | 부작용 상세 | `reaction_details` | string | ❌ | 부작용 설명 |
| 다음 접종 예정일 | 다음 접종일 | `next_vaccination_due` | string | ❌ | YYYY-MM-DD 형식 |
| 비용 | 접종 비용 | `cost` | float | ❌ | 원 단위 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 9. ⚖️ 체중측정 기록 (weight)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 체중측정 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 측정 시간 | 체중측정 시간 | `measurement_time` | string | ❌ | HH:MM:SS 형식 |
| 체중 | 체중 | `weight` | float | ❌ | 킬로그램(kg) 단위 |
| 측정 방법 | 측정 방법 | `measurement_method` | string | ❌ | 전자저울/체척자/목측 |
| 체형점수 | 체형점수 | `body_condition_score` | float | ❌ | 1-5 점수 |
| 기갑고 | 기갑고 | `height_withers` | float | ❌ | 센티미터(cm) 단위 |
| 체장 | 체장 | `body_length` | float | ❌ | 센티미터(cm) 단위 |
| 흉위 | 흉위 | `chest_girth` | float | ❌ | 센티미터(cm) 단위 |
| 증체율 | 증체율 | `growth_rate` | float | ❌ | kg/일 단위 |
| 목표체중 | 목표 체중 | `target_weight` | float | ❌ | 킬로그램(kg) 단위 |
| 체중 등급 | 체중 등급 | `weight_category` | string | ❌ | 체중 분류 |
| 측정자 | 측정 담당자 | `measurer` | string | ❌ | 측정자 이름 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

### 10. 🩺 치료 기록 (treatment)

**Firebase 경로**: `cow_detailed_records/{record_id}/record_data/`

| 한국어 필드명 | 필드 설명 | Firebase 필드명 | 데이터 타입 | 필수 여부 | 비고 |
|---------------|-----------|-----------------|-------------|-----------|------|
| 젖소 ID | 젖소 고유 식별자 | `cow_id` | string | ✅ | 기본 필드 |
| 기록 날짜 | 치료 날짜 | `record_date` | string | ✅ | YYYY-MM-DD 형식 |
| 치료 시간 | 치료 시간 | `treatment_time` | string | ❌ | HH:MM:SS 형식 |
| 치료 종류 | 치료 유형 | `treatment_type` | string | ❌ | 치료 분류 |
| 증상 | 증상 목록 | `symptoms` | array | ❌ | 문자열 배열 |
| 진단명 | 진단명 | `diagnosis` | string | ❌ | 진단 결과 |
| 사용약물 | 사용 약물 | `medication_used` | array | ❌ | 문자열 배열 |
| 용법용량 정보 | 용법용량 | `dosage_info` | object | ❌ | 키-값 쌍 객체 |
| 치료 방법 | 치료 방법 | `treatment_method` | string | ❌ | 치료 기법 |
| 치료 기간 | 치료 기간 | `treatment_duration` | integer | ❌ | 일 단위 |
| 수의사명 | 수의사 | `veterinarian` | string | ❌ | 담당 수의사 |
| 치료 반응 | 치료 반응 | `treatment_response` | string | ❌ | 치료 효과 |
| 부작용 | 부작용 | `side_effects` | string | ❌ | 부작용 설명 |
| 추후 관찰 필요 | 추후 관찰 | `follow_up_required` | boolean | ❌ | true/false |
| 추후 관찰일 | 추후 관찰일 | `follow_up_date` | string | ❌ | YYYY-MM-DD 형식 |
| 치료비용 | 치료 비용 | `treatment_cost` | float | ❌ | 원 단위 |
| 휴약기간 | 휴약 기간 | `withdrawal_period` | integer | ❌ | 일 단위 |
| 비고 | 특이사항 | `notes` | string | ❌ | 기타 메모 |

---

## 🤖 AI 챗봇 활용 예시

### 사용자 질문 예시와 활용 필드

#### 1. 착유량 관련 질문
```
사용자: "002123456789번 소 최근 착유량 어떻게 돼?"
활용 필드: milk_yield, record_date, fat_percentage, protein_percentage
```

#### 2. 건강 상태 관련 질문
```
사용자: "꽃분이 체온이 몇 도야?"
활용 필드: body_temperature, record_date, abnormal_symptoms
```

#### 3. 번식 관리 관련 질문
```
사용자: "발정기인 소들 누구야?"
활용 필드: estrus_intensity, record_date, breeding_planned
```

#### 4. 치료 이력 관련 질문
```
사용자: "최근에 치료받은 소들 있어?"
활용 필드: diagnosis, treatment_type, veterinarian, treatment_cost
```

---

## 📋 데이터 접근 패턴

### Firebase 쿼리 예시

```javascript
// 특정 젖소의 최근 착유 기록 조회
db.collection('cow_detailed_records')
  .where('cow_id', '==', cowId)
  .where('record_type', '==', 'milking')
  .where('is_active', '==', true)
  .orderBy('record_date', 'desc')
  .limit(10)

// 특정 농장의 건강검진 기록 조회
db.collection('cow_detailed_records')
  .where('farm_id', '==', farmId)
  .where('record_type', '==', 'health_check')
  .where('is_active', '==', true)
  .orderBy('created_at', 'desc')
```

---

## 🔍 검색 키워드 매핑

AI 챗봇에서 사용자 질문을 해석할 때 유용한 키워드 매핑:

### 착유 관련 키워드
- `착유량`, `우유`, `milk` → `milk_yield`
- `유지방`, `지방` → `fat_percentage`
- `유단백`, `단백질` → `protein_percentage`
- `체세포`, `체세포수` → `somatic_cell_count`

### 건강 관련 키워드
- `체온`, `열` → `body_temperature`
- `맥박`, `심박수` → `heart_rate`
- `호흡`, `호흡수` → `respiratory_rate`
- `체형점수`, `BCS` → `body_condition_score`

### 번식 관련 키워드
- `발정`, `estrus` → `estrus_intensity`, `estrus_duration`
- `인공수정`, `AI` → `insemination_time`, `semen_quality`
- `임신`, `임신감정` → `check_result`, `expected_calving_date`
- `분만`, `출산` → `calving_difficulty`, `calf_count`

### 치료 관련 키워드
- `치료`, `병원`, `수의사` → `diagnosis`, `veterinarian`
- `약물`, `약` → `medication_used`, `dosage_info`
- `백신`, `예방접종` → `vaccine_name`, `vaccination_time`

---

## 📊 데이터 유효성 검증

### 필수 유효성 검사 규칙

1. **날짜 형식**: 모든 날짜는 `YYYY-MM-DD` 형식
2. **시간 형식**: 모든 시간은 `HH:MM:SS` 형식
3. **착유량**: 0보다 큰 값만 허용
4. **체세포수**: 0-10,000,000 범위
5. **백분율**: 0% 이상 값만 허용
6. **배열 데이터**: JSON 배열 형태로 저장

### 데이터 타입 변환 규칙

- **문자열**: 모든 텍스트 데이터
- **숫자**: 정수(integer) 또는 실수(float)
- **불린**: true/false 값
- **배열**: 여러 항목의 목록
- **객체**: 키-값 쌍의 구조화된 데이터

---