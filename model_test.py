# #!/usr/bin/env python3
# """
# 무료 티어용 단계별 안전한 성능 테스트
# """

# import joblib
# import numpy as np
# import time
# import warnings
# import psutil
# import sys

# # sklearn 경고 무시
# warnings.filterwarnings('ignore', message='X does not have valid feature names')

# def check_memory_safety(stage_name, threshold=85):
#     """메모리 안전성 체크"""
#     memory = psutil.virtual_memory()
#     print(f"  📊 {stage_name} 메모리: {memory.percent:.1f}%")
    
#     if memory.percent > threshold:
#         print(f"❌ 메모리 {memory.percent:.1f}% > {threshold}% - 테스트 중단!")
#         sys.exit(1)
    
#     return memory.percent

# def safe_staged_test():
#     """단계별 안전한 성능 테스트"""
#     print("⚡ 무료 티어용 단계별 안전한 성능 테스트\n")
    
#     # 초기 시스템 상태
#     initial_memory = check_memory_safety("시작 전")
    
#     # 테스트 데이터
#     test_data = np.array([[2, 7.5, 38.5, 3.8, 3.2, 3.5, 6, 1]])
    
#     # ========== 1. 모델 로드 시간 측정 (1번만) ==========
#     print("\n📦 1단계: 모델 로드 시간 측정 (1번)")
    
#     start = time.time()
#     model = joblib.load('models/1_random_forest.pkl')
#     scaler = joblib.load('models/1_scaler.pkl')
#     model_load_time = (time.time() - start) * 1000
    
#     print(f"  ⏱️ 모델 로드: {model_load_time:.0f}ms ({model_load_time/1000:.2f}초)")
    
#     # 로드 후 메모리 확인
#     after_load_memory = check_memory_safety("모델 로드 후", threshold=90)
#     memory_increase = after_load_memory - initial_memory
#     print(f"  📈 메모리 증가: {memory_increase:.1f}%")
    
#     # 데이터 전처리
#     scaled_data = scaler.transform(test_data)
#     print(f"  ✅ 모델 로드 완료 (트리 {len(model.estimators_)}개)")
    
#     # ========== 2. 일반 추론 3번 측정 ==========
#     print(f"\n🚀 2단계: 일반 추론 시간 (3번 측정)")
    
#     inference_times = []
#     for i in range(3):
#         start = time.time()
#         prediction = model.predict(scaled_data)[0]
#         end = time.time()
#         inference_times.append((end - start) * 1000)
#         print(f"  측정 {i+1}: {inference_times[i]:.2f}ms")
#         time.sleep(0.1)  # CPU 쿨다운
    
#     avg_inference_3 = sum(inference_times) / len(inference_times)
#     print(f"  📊 3번 평균: {avg_inference_3:.2f}ms ({avg_inference_3/1000:.3f}초)")
#     print(f"  🔮 예측값: {prediction:.2f}L")
    
#     # 메모리 체크
#     check_memory_safety("3번 추론 후")
    
#     # ========== 3. 일반 추론 10번 측정 (메모리 허용 시) ==========
#     print(f"\n🚀 3단계: 일반 추론 시간 (10번 측정)")
    
#     current_memory = psutil.virtual_memory().percent
#     if current_memory > 80:
#         print(f"❌ 메모리 {current_memory:.1f}% > 80% - 10번 측정 건너뜀")
#         avg_inference_10 = "측정 안함"
#     else:
#         inference_times_10 = []
#         for i in range(10):
#             start = time.time()
#             prediction = model.predict(scaled_data)[0]
#             end = time.time()
#             inference_times_10.append((end - start) * 1000)
            
#             if (i + 1) % 3 == 0:  # 3번마다 출력
#                 print(f"  측정 {i+1}: {inference_times_10[i]:.2f}ms")
            
#             time.sleep(0.05)  # CPU 쿨다운
        
#         avg_inference_10 = sum(inference_times_10) / len(inference_times_10)
#         print(f"  📊 10번 평균: {avg_inference_10:.2f}ms ({avg_inference_10/1000:.3f}초)")
        
#         # 메모리 체크
#         check_memory_safety("10번 추론 후")
    
#     # ========== 4. 확신도 계산 (매우 제한적) ==========
#     print(f"\n🔍 4단계: 확신도 계산 테스트")
    
#     current_memory = psutil.virtual_memory().percent
#     if current_memory > 75:
#         print(f"❌ 메모리 {current_memory:.1f}% > 75% - 확신도 테스트 건너뜀")
#         confidence_time = "측정 안함"
#         estimated_full_confidence = "측정 안함"
#     else:
#         print(f"  🧪 샘플 테스트 (10개 트리만)")
        
#         start = time.time()
        
#         # 일반 예측
#         prediction = model.predict(scaled_data)[0]
        
#         # 확신도 계산 (10개 트리만 샘플링)
#         import random
#         sample_trees = random.sample(model.estimators_, 10)
        
#         tree_predictions = []
#         for tree in sample_trees:
#             tree_pred = tree.predict(scaled_data)[0]
#             tree_predictions.append(tree_pred)
        
#         std_dev = np.std(tree_predictions)
#         mean_pred = np.mean(tree_predictions)
#         cv = std_dev / mean_pred if mean_pred > 0 else 0
#         confidence = (1 - cv) * 100
        
#         end = time.time()
#         confidence_time = (end - start) * 1000
        
#         print(f"  ⏱️ 10개 트리 시간: {confidence_time:.2f}ms ({confidence_time/1000:.3f}초)")
#         print(f"  🎯 확신도: {confidence:.0f}%")
        
#         # 전체 100개 트리 예상 시간
#         estimated_full_confidence = confidence_time * 10
#         print(f"  📈 100개 트리 예상: {estimated_full_confidence:.0f}ms ({estimated_full_confidence/1000:.1f}초)")
        
#         # 메모리 체크
#         check_memory_safety("확신도 계산 후")
    
#     # ========== 5. 종합 결과 ==========
#     print(f"\n📊 종합 결과 요약")
#     print(f"{'='*60}")
#     print(f"{'단계':<20} {'시간(ms)':<15} {'시간(초)':<15} {'상태'}")
#     print(f"{'-'*60}")
#     print(f"{'모델 로드':<20} {model_load_time:.0f}ms{'':<10} {model_load_time/1000:.2f}초{'':<10} ✅")
#     print(f"{'추론 3번 평균':<20} {avg_inference_3:.2f}ms{'':<10} {avg_inference_3/1000:.3f}초{'':<10} ✅")
    
#     if isinstance(avg_inference_10, str):
#         print(f"{'추론 10번 평균':<20} {avg_inference_10:<15} {avg_inference_10:<15} ❌")
#     else:
#         print(f"{'추론 10번 평균':<20} {avg_inference_10:.2f}ms{'':<10} {avg_inference_10/1000:.3f}초{'':<10} ✅")
    
#     if isinstance(confidence_time, str):
#         print(f"{'확신도 (샘플)':<20} {confidence_time:<15} {confidence_time:<15} ❌")
#         print(f"{'확신도 (전체 예상)':<20} {estimated_full_confidence:<15} {estimated_full_confidence:<15} ❌")
#     else:
#         print(f"{'확신도 (샘플)':<20} {confidence_time:.2f}ms{'':<10} {confidence_time/1000:.3f}초{'':<10} ✅")
#         print(f"{'확신도 (전체 예상)':<20} {estimated_full_confidence:.0f}ms{'':<10} {estimated_full_confidence/1000:.1f}초{'':<10} {'✅' if estimated_full_confidence < 2000 else '❌'}")
    
#     # ========== 6. 무료 티어 권장사항 ==========
#     print(f"\n💡 무료 티어 권장사항")
#     print(f"{'='*60}")
    
#     if isinstance(avg_inference_10, str):
#         print("❌ 기본 추론도 메모리 부족으로 불안정")
#         print("   → 서버 업그레이드 필수")
#     elif avg_inference_3 > 100:
#         print("❌ 추론 시간이 너무 느림 (>100ms)")
#         print("   → 서버 업그레이드 권장")
#     elif isinstance(estimated_full_confidence, str) or estimated_full_confidence > 5000:
#         print("✅ 기본 예측은 가능")
#         print("❌ 확신도 계산 불가 (메모리 부족 또는 >5초)")
#         print("   → 확신도 기능 제거 권장")
#         print("   → 정확도 82%만 표시")
#     elif estimated_full_confidence > 1000:
#         print("✅ 기본 예측 가능")
#         print("⚠️ 확신도 계산 느림 (>1초)")
#         print("   → 10개 트리 샘플링 방식 권장")
#         print("   → 또는 확신도 제거 고려")
#     else:
#         print("🎉 모든 기능 사용 가능!")
#         print("   → 확신도 포함 서비스 가능")
    
#     # ========== 7. 최종 메모리 상태 ==========
#     final_memory = psutil.virtual_memory()
#     print(f"\n🏁 최종 시스템 상태")
#     print(f"  초기 메모리: {initial_memory:.1f}%")
#     print(f"  최종 메모리: {final_memory.percent:.1f}%")
#     print(f"  총 증가량: {final_memory.percent - initial_memory:.1f}%")

# if __name__ == "__main__":
#     try:
#         safe_staged_test()
#     except KeyboardInterrupt:
#         print("\n\n⏹️ 사용자가 테스트 중단")
#     except SystemExit:
#         print("\n\n🛑 메모리 부족으로 안전 중단")
#     except Exception as e:
#         print(f"\n\n❌ 테스트 실패: {e}")
#         import traceback
#         traceback.print_exc()

#!/usr/bin/env python3
"""
모델 로드만 하는 안전한 테스트 (98% 초과 시 즉시 중단)
"""

import joblib
import time
import psutil
import sys
import os

def check_resources():
    """실시간 리소스 체크"""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    print(f"CPU: {cpu:5.1f}%, 메모리: {memory.percent:5.1f}%", end=" ")
    
    if cpu > 98 or memory.percent > 98:
        print(f"\n❌ 위험! CPU {cpu:.1f}% 또는 메모리 {memory.percent:.1f}% > 98% - 즉시 중단!")
        sys.exit(1)
    
    return cpu, memory.percent

def simple_model_load_test():
    """모델 로드만 하는 간단한 테스트"""
    print("🔧 모델 로드 테스트 (98% 초과 시 자동 중단)\n")
    
    # 초기 상태
    print("📊 초기 상태 확인...")
    initial_cpu, initial_memory = check_resources()
    print("✅ 안전")
    
    # 파일 존재 확인
    print("\n📁 파일 존재 확인...")
    model_path = "models/1_random_forest.pkl"
    scaler_path = "models/1_scaler.pkl"
    
    if not os.path.exists(model_path):
        print(f"❌ 모델 파일 없음: {model_path}")
        return
    
    if not os.path.exists(scaler_path):
        print(f"❌ 스케일러 파일 없음: {scaler_path}")
        return
    
    # 파일 크기 확인
    model_size = os.path.getsize(model_path) / 1024 / 1024
    scaler_size = os.path.getsize(scaler_path) / 1024 / 1024
    
    print(f"  모델 파일: {model_size:.1f}MB")
    print(f"  스케일러 파일: {scaler_size:.1f}MB")
    print(f"  총 크기: {model_size + scaler_size:.1f}MB")
    
    # 메모리 여유 공간 확인
    available_memory = psutil.virtual_memory().available / 1024 / 1024
    print(f"  사용 가능 메모리: {available_memory:.0f}MB")
    
    if model_size > available_memory * 0.8:
        print(f"❌ 메모리 부족! 모델 크기 {model_size:.0f}MB > 사용가능 {available_memory*.8:.0f}MB")
        return
    
    print("✅ 파일 확인 완료")
    
    # 스케일러 로드 (작은 파일부터)
    print(f"\n🔧 1단계: 스케일러 로드 중... ({scaler_size:.1f}MB)")
    start_time = time.time()
    
    try:
        # 로드 중 실시간 모니터링
        print("  진행 중: ", end="")
        scaler = joblib.load(scaler_path)
        
        scaler_load_time = time.time() - start_time
        cpu, memory = check_resources()
        print(f"\n  ✅ 스케일러 로드 완료: {scaler_load_time:.2f}초")
        
    except Exception as e:
        print(f"\n  ❌ 스케일러 로드 실패: {e}")
        return
    
    # 모델 로드 (큰 파일)
    print(f"\n🔧 2단계: 모델 로드 중... ({model_size:.1f}MB)")
    print("  ⚠️ 이 단계에서 시간이 오래 걸릴 수 있습니다")
    
    start_time = time.time()
    
    try:
        # 로드 시작
        print("  진행률: [", end="")
        sys.stdout.flush()
        
        # 모델 로드 (백그라운드에서 리소스 모니터링)
        model = joblib.load(model_path)
        
        model_load_time = time.time() - start_time
        print("]")
        
        cpu, memory = check_resources()
        print(f"\n  ✅ 모델 로드 완료: {model_load_time:.2f}초")
        
        # 모델 정보
        if hasattr(model, 'estimators_'):
            print(f"  📊 RandomForest: {len(model.estimators_)}개 트리")
        
    except Exception as e:
        print(f"]\n  ❌ 모델 로드 실패: {e}")
        return
    
    # 최종 상태
    print(f"\n📊 최종 상태:")
    final_cpu, final_memory = check_resources()
    print("")
    
    print(f"  초기: CPU {initial_cpu:.1f}%, 메모리 {initial_memory:.1f}%")
    print(f"  최종: CPU {final_cpu:.1f}%, 메모리 {final_memory:.1f}%")
    print(f"  증가: CPU {final_cpu-initial_cpu:+.1f}%, 메모리 {final_memory-initial_memory:+.1f}%")
    
    # 총 시간
    total_time = scaler_load_time + model_load_time
    print(f"\n⏱️ 총 로드 시간:")
    print(f"  스케일러: {scaler_load_time:.2f}초")
    print(f"  모델: {model_load_time:.2f}초")
    print(f"  합계: {total_time:.2f}초")
    
    # 간단한 테스트
    print(f"\n🧪 간단한 동작 테스트...")
    try:
        import numpy as np
        test_data = np.array([[2, 7.5, 38.5, 3.8, 3.2, 3.5, 6, 1]])
        scaled_data = scaler.transform(test_data)
        
        test_start = time.time()
        prediction = model.predict(scaled_data)[0]
        test_time = (time.time() - test_start) * 1000
        
        print(f"  ✅ 예측 테스트 성공: {prediction:.2f}L ({test_time:.1f}ms)")
        
    except Exception as e:
        print(f"  ❌ 예측 테스트 실패: {e}")
    
    # 결론
    print(f"\n🎯 결론:")
    if total_time < 1:
        print(f"  🎉 매우 빠름 ({total_time:.2f}초) - 서버 시작 시 모델 로드 권장")
    elif total_time < 5:
        print(f"  ✅ 적당함 ({total_time:.2f}초) - 서버 시작 시 모델 로드 가능")
    elif total_time < 10:
        print(f"  ⚠️ 느림 ({total_time:.2f}초) - 첫 요청 시 지연 고려")
    else:
        print(f"  ❌ 매우 느림 ({total_time:.2f}초) - 서버 업그레이드 필요")
    
    if final_memory > 90:
        print(f"  ❌ 메모리 부족 ({final_memory:.1f}%) - 다른 프로세스와 충돌 위험")
    elif final_memory > 80:
        print(f"  ⚠️ 메모리 높음 ({final_memory:.1f}%) - 모니터링 필요")
    else:
        print(f"  ✅ 메모리 안전 ({final_memory:.1f}%)")

if __name__ == "__main__":
    try:
        simple_model_load_test()
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 테스트 중단")
    except SystemExit:
        print("\n\n🛑 리소스 98% 초과로 안전 중단")
    except Exception as e:
        print(f"\n\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()