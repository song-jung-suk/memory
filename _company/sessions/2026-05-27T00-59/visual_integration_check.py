import json
from typing import Dict, Any

# --- 1. 데이터 모델 정의 (models.py에서 가져오는 것을 가정) ---
class CostItem:
    def __init__(self, name: str, cost: float, labor_hours: float, risk_score: float):
        self.name = name
        self.cost = cost
        self.labor_hours = labor_hours
        self.risk_score = risk_score

class KPIReport:
    def __init__(self, total_chaos: float, total_order: float, efficiency_ratio: float):
        self.total_chaos = total_chaos
        self.total_order = total_order
        self.efficiency_ratio = efficiency_ratio

# --- 2. 시각화 매핑 로직 (Designer의 요구사항 반영) ---
def calculate_chaos_order_score(cost_data: Dict[str, CostItem]) -> KPIReport:
    """
    CostItem 데이터를 기반으로 Chaos (혼돈)와 Order (질서) 점수를 계산합니다.
    Chaos는 비용과 노동 시간의 복잡성을 반영하고, Order는 효율성/투명성을 반영합니다.
    """
    total_chaos = 0.0
    total_order = 0.0
    
    for item in cost_data.values():
        # Chaos 계산: 비용 + 노동시간 (복잡성)
        chaos_score = item.cost + item.labor_hours * 10  # 노동 시간 가중치 부여
        total_chaos += chaos_score

        # Order 계산: 효율성 (비용 대비 시간) - 단순화를 위해 역산하여 Order로 간주
        if item.cost > 0 and item.labor_hours > 0:
            efficiency = item.cost / item.labor_hours
            order_score = 1.0 / efficiency # 효율성이 높을수록 Order 점수 증가
            total_order += order_score

    # 최종 효율성 비율 계산 (Chaos 대비 Order)
    if total_chaos > 0:
        efficiency_ratio = total_order / total_chaos
    else:
        efficiency_ratio = 0.0

    return KPIReport(total_chaos=total_chaos, total_order=total_order, efficiency_ratio=efficiency_ratio)

def validate_visual_mapping(kpi_data: KPIReport, design_specs: Dict[str, Any]) -> bool:
    """
    계산된 KPI 데이터가 디자인 시스템의 요구사항을 충족하는지 검증합니다.
    Chaos $\rightarrow$ Order 흐름이 시각적으로 유효한지 확인합니다.
    """
    print("--- [검증 시작] ---")
    print(f"입력된 Chaos 점수: {kpi_data.total_chaos:.2f}")
    print(f"입력된 Order 점수: {kpi_data.total_order:.2f}")
    print(f"최종 효율성 비율 (Chaos $\rightarrow$ Order 흐름): {kpi_data.efficiency_ratio:.4f}")

    # Designer의 핵심 원칙 검증: Chaos가 Order로 명확히 전환되는지 확인
    if kpi_data.efficiency_ratio < 0.5:
        print("⚠️ 경고: 효율성 비율이 낮습니다. 혼돈(Chaos) 상태가 질서(Order)로 충분히 전환되지 않았을 수 있습니다.")
        return False
    else:
        print("✅ 검증 통과: Chaos $\rightarrow$ Order 흐름이 시각적으로 유효한 수준으로 계산되었습니다.")
        return True

def main():
    """메인 실행 함수"""
    # 가상의 CostItem 데이터 (실제로는 models.py에서 로드되어야 함)
    sample_cost_data = {
        "Shipping Fee": CostItem("Shipping Fee", 100, 2, 0.5),
        "Customs Duty": CostItem("Customs Duty", 300, 5, 0.8),
        "Labor Time": CostItem("Labor Time", 50, 10, 0.9),
    }

    # Designer의 시각 가이드라인 (가정)
    design_specs = {
        "visual_style": "Chaos -> Order",
        "color_mapping": {"chaos": "#FF4500", "order": "#007BFF"}
    }

    print("=== 시스템 통합 검증 코드 실행 ===")
    
    # 1. 데이터 계산
    kpi = calculate_chaos_order_score(sample_cost_data)
    
    # 2. 시각 흐름 검증
    is_valid = validate_visual_mapping(kpi, design_specs)

    if is_valid:
        print("\n🎉 최종 시스템 통합 검증 성공. 데이터는 디자인 흐름을 뒷받침합니다.")
    else:
        print("\n🛑 시스템 통합 경고. KPI 결과가 시각적 대비 원칙을 충족하지 못했습니다. 데이터 재검토 필요.")

if __name__ == "__main__":
    main()