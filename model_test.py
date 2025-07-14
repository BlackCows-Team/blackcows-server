#!/usr/bin/env python3
"""
무료 티어용 단계별 안전한 성능 테스트
"""

import joblib
import numpy as np
import time
import warnings
import psutil
import sys

# sklearn 경고 무시
warnings.filterwarnings('ignore', message='X does not have valid feature names')

def check_memory_safety(stage_name, threshold=85):
    """메모리 안전성 체크"""
    memory = psutil.virtual_memory()
    print(f"  📊 {stage_name} 메모리: {memory.percent:.1f}%")
    
    if memory.percent > threshold:
        print(f"❌ 메모리 {memory.percent:.1f}% > {threshold}% - 테스트 중단!")
        sys.exit(1)
    
    return memory.percent

def inference_time_test(model, scaled_data, total_runs=100):
    """1, 50, 100번 추론까지의 누적 소요 시간 및 전체 소요 시간 출력"""
    inference_times = []
    print(f"\n🚀 추론 시간 측정 (총 {total_runs}번)")
    start_total = time.time()
    for i in range(total_runs):
        start = time.time()
        prediction = model.predict(scaled_data)[0]
        end = time.time()
        inference_times.append((end - start) * 1000)
        if i == 0:
            elapsed_1 = time.time() - start_total
            print(f"  1번 추론까지 소요 시간: {elapsed_1*1000:.2f}ms ({elapsed_1:.3f}초)")
        if i == 49:
            elapsed_50 = time.time() - start_total
            print(f"  50번 추론까지 소요 시간: {elapsed_50*1000:.2f}ms ({elapsed_50:.3f}초)")
        if i == 99:
            elapsed_100 = time.time() - start_total
            print(f"  100번 추론까지 소요 시간: {elapsed_100*1000:.2f}ms ({elapsed_100:.3f}초)")
    end_total = time.time()
    total_elapsed = end_total - start_total
    print(f"\n🔢 100번 추론 전체 소요 시간: {total_elapsed:.3f}초")
    return inference_times, total_elapsed, elapsed_1, elapsed_50, elapsed_100

def safe_staged_test():
    """단계별 안전한 성능 테스트 (수정됨: 추론 1, 50, 100번 및 전체 시간)"""
    print("⚡ 무료 티어용 단계별 안전한 성능 테스트\n")
    
    # 초기 시스템 상태
    initial_memory = check_memory_safety("시작 전")
    
    # 테스트 데이터
    test_data = np.array([[2, 7.5, 38.5, 3.8, 3.2, 3.5, 6, 1]])
    
    # ========== 1. 모델 로드 시간 측정 (1번만) ==========
    print("\n📦 1단계: 모델 로드 시간 측정 (1번)")
    
    start = time.time()
    model = joblib.load('models/1_random_forest.pkl')
    scaler = joblib.load('models/1_scaler.pkl')
    model_load_time = (time.time() - start) * 1000
    
    print(f"  ⏱️ 모델 로드: {model_load_time:.0f}ms ({model_load_time/1000:.2f}초)")
    
    # 로드 후 메모리 확인
    after_load_memory = check_memory_safety("모델 로드 후", threshold=90)
    memory_increase = after_load_memory - initial_memory
    print(f"  📈 메모리 증가: {memory_increase:.1f}%")
    
    # 데이터 전처리
    scaled_data = scaler.transform(test_data)
    print(f"  ✅ 모델 로드 완료 (트리 {len(model.estimators_)}개)")
    
    # ========== 2. 추론 시간 측정 (1, 50, 100번) ==========
    inference_times, total_elapsed, elapsed_1, elapsed_50, elapsed_100 = inference_time_test(model, scaled_data, total_runs=100)
    
    # ========== 3. 종합 결과 ==========
    print(f"\n📊 종합 결과 요약")
    print(f"{'='*60}")
    print(f"{'단계':<20} {'시간(ms)':<15} {'시간(초)':<15} {'상태'}")
    print(f"{'-'*60}")
    print(f"{'모델 로드':<20} {model_load_time:.0f}ms{'':<10} {model_load_time/1000:.2f}초{'':<10} ✅")
    print(f"{'1번 추론':<20} {elapsed_1*1000:.2f}ms{'':<10} {elapsed_1:.3f}초{'':<10} ✅")
    print(f"{'50번 누적':<20} {elapsed_50*1000:.2f}ms{'':<10} {elapsed_50:.3f}초{'':<10} ✅")
    print(f"{'100번 누적':<20} {elapsed_100*1000:.2f}ms{'':<10} {elapsed_100:.3f}초{'':<10} ✅")
    print(f"{'100번 전체':<20} {'-':<15} {total_elapsed:.3f}초{'':<10} ✅")
    
    # ========== 4. 최종 메모리 상태 ==========
    final_memory = psutil.virtual_memory()
    print(f"\n🏁 최종 시스템 상태")
    print(f"  초기 메모리: {initial_memory:.1f}%")
    print(f"  최종 메모리: {final_memory.percent:.1f}%")
    print(f"  총 증가량: {final_memory.percent - initial_memory:.1f}%")

if __name__ == "__main__":
    try:
        safe_staged_test()
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 테스트 중단")
    except SystemExit:
        print("\n\n🛑 메모리 부족으로 안전 중단")
    except Exception as e:
        print(f"\n\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()