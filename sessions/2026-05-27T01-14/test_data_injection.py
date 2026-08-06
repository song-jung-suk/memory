import json
from models import CostItem, KPIReport
from cost_tracker import process_cost_items

# --- 1. 테스트용 데이터 정의 (실제 입력 시 이 부분을 교체할 예정) ---
TEST_COST_ITEMS = [
    {"id": "C001", "name": "Product A Sourcing", "cost": 500, "time_spent_h": 10},
    {"id": "C002", "name": "Logistics Fee", "cost": 300, "time_spent_h": 5},
]

# --- 2. 데이터 입력 및 처리 로직 실행 ---
def run_test():
    print("--- CostItem 데이터 주입 시작 ---")
    
    # 실제 시스템이 이 데이터를 받아 KPI를 계산하는지 검증
    results = process_cost_items(TEST_COST_ITEMS)
    
    print("\n✅ CostItem 처리 결과:")
    print(json.dumps(results, indent=4, ensure_ascii=False))
    
    # 시각화 매핑 검증을 위한 중간 결과 확인
    if results:
        print("\n📊 KPIReport 생성 성공. 시각화 매핑 준비 완료.")
    else:
        print("\n❌ CostItem 처리 실패. 로직 오류 발생.")

if __name__ == "__main__":
    run_test()