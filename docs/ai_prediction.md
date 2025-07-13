# AI 착유량 예측 기능 배포 체크리스트

## 📋 사전 준비사항

### 1. AWS S3 설정
- [ ] S3 버킷 생성 (`blackcows-ml-models`)
- [ ] 모델 파일 업로드 (`1_random_forest.pkl`, `1_scaler.pkl`)
- [ ] IAM 역할/정책 설정 (EC2에서 S3 접근 권한)
- [ ] 버킷 정책 확인

### 2. 환경변수 설정
- [ ] `AWS_S3_BUCKET_NAME=blackcows-ml-models`
- [ ] `AWS_DEFAULT_REGION=ap-northeast-2`
- [ ] AWS 자격증명 설정 (IAM 역할 권장)

### 3. Python 패키지 설치
- [ ] numpy, pandas, scikit-learn, joblib
- [ ] boto3, botocore
- [ ] scipy

## 🚀 배포 순서

### 1단계: 코드 배포
```bash
# 1. 새로운 파일들 추가
git add routers/ai_prediction.py
git add schemas/ai_prediction.py
git add services/ai_prediction_service.py

# 2. main.py 라우터 추가
# app.include_router(ai_prediction.router, prefix="/api/ai-prediction")

# 3. requirements.txt 업데이트

# 4. Git 커밋 및 푸시
git commit -m "Add AI milk yield prediction feature"
git push origin main
```

### 2단계: 서버 배포
```bash
# GitHub Actions를 통한 자동 배포 또는 수동 배포
ssh ubuntu@52.78.212.96
cd ~/blackcows-server
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
# 서버 재시작
```

### 3단계: 테스트
- [ ] 모델 상태 확인: `/api/ai-prediction/test/model-health`
- [ ] 샘플 예측 테스트: `/api/ai-prediction/test/predict-sample`
- [ ] 실제 예측 API 테스트
- [ ] 인증이 필요한 엔드포인트 테스트

## 🔧 트러블슈팅

### 일반적인 문제들

#### 1. S3 연결 실패
**증상:** `AWS S3 연결에 실패했습니다`
**해결방법:**
- IAM 역할 확인
- 버킷 이름 및 리전 확인
- 네트워크 연결 상태 확인

#### 2. 모델 파일 로드 실패
**증상:** `AI 모델 로드에 실패했습니다`
**해결방법:**
- S3에 모델 파일이 올바르게 업로드되었는지 확인
- 파일 경로 확인 (`models/1_random_forest.pkl`)
- 파일 권한 확인

#### 3. 패키지 호환성 문제
**증상:** `ImportError` 또는 `ModuleNotFoundError`
**해결방법:**
- scikit-learn 버전 확인 (모델과 호환되는 버전)
- 가상환경에서 패키지 재설치
- `pip freeze`로 설치된 패키지 확인

#### 4. 메모리 부족
**증상:** 서버 응답 지연 또는 OutOfMemory 에러
**해결방법:**
- 모델 캐싱 활성화 확인
- EC2 인스턴스 크기 업그레이드 고려
- 불필요한 프로세스 종료

## 📊 모니터링

### 확인해야 할 지표들
- [ ] API 응답 시간 (목표: < 2초)
- [ ] 예측 정확도 (목표: > 80%)
- [ ] 메모리 사용량
- [ ] S3 API 호출 횟수

### 로그 확인
```bash
# 서버 로그 확인
tmux attach-session -t 0
# 또는
tail -f /var/log/your-app/app.log
```

### 성능 최적화
- [ ] 모델 캐싱 적용 (1시간)
- [ ] 배치 예측에서 병렬 처리
- [ ] 데이터베이스 인덱스 최적화

## 🎯 성공 기준

### 기능 테스트
- [ ] 개별 예측 API 정상 작동
- [ ] 배치 예측 API 정상 작동
- [ ] 예측 이력 조회 정상 작동
- [ ] 피드백 기능 정상 작동

### 성능 테스트
- [ ] 단일 예측 응답시간 < 2초
- [ ] 배치 예측(10개) 응답시간 < 10초
- [ ] 동시 사용자 10명 처리 가능

### 안정성 테스트
- [ ] 24시간 연속 운영 안정성
- [ ] 잘못된 입력값 처리
- [ ] 네트워크 오류 시 적절한 에러 메시지

## 📱 프론트엔드 연동 가이드

### Flutter/React에서 사용할 API 엔드포인트
1. **예측 요청**: `POST /api/ai-prediction/milk-yield/predict`
2. **예측 이력**: `GET /api/ai-prediction/milk-yield/cow/{cow_id}/history`
3. **농장 분석**: `GET /api/ai-prediction/milk-yield/farm/analytics`
4. **권장사항**: `GET /api/ai-prediction/insights/recommendations`

### 예제 JavaScript 코드
```javascript
// 착유량 예측 요청
const predictMilkYield = async (cowData) => {
  const response = await fetch('/api/ai-prediction/milk-yield/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(cowData)
  });
  return await response.json();
};
```

## ⚠️ 주의사항

1. **데이터 보안**: 예측 데이터는 민감한 농장 정보이므로 적절한 인증/인가 필요
2. **모델 버전 관리**: 새로운 모델 배포 시 기존 예측과의 일관성 고려
3. **비용 관리**: AWS S3 API 호출 비용 모니터링
4. **백업**: 모델 파일과 예측 데이터의 정기적인 백업

## 🔄 향후 개선사항

- [ ] 모델 자동 재학습 파이프라인
- [ ] A/B 테스트를 통한 모델 성능 비교
- [ ] 실시간 데이터 스트리밍 연동
- [ ] 더 정교한 특성 엔지니어링
- [ ] 다른 ML 모델 (XGBoost, Neural Networks) 실험

