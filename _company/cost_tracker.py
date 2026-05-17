"""
Cost Tracker Module: 노동 시간 및 리스크 기반 비용 추적 시스템 모듈.
혼돈(Chaos) 데이터를 질서(Order)로 변환하는 핵심 로직을 포함합니다.
"""
import datetime
from typing import List, Dict, Any
from models import CostItem, KPIReport # models.py에서 정의된 모델들을 임포트한다고 가정

class CostTracker:
    """
    노동 시간과 리스크를 추적하고 KPI 보고서를 생성하는 클래스.
    Chaos -> Order 프레임워크를 기반으로 비용 추적을 자동화합니다.
    """
    def __init__(self, cost_items: List[CostItem], kpi_reports: List[KPIReport]):
        self.cost_items = cost_items
        self.kpi_reports = kpi_reports
        print("CostTracker 초기화 완료: CostItem 및 KPIReport 데이터 로드.")

    def calculate_labor_cost(self, items: List[CostItem], rate_per_hour: float) -> Dict[str, Any]:
        """
        주어진 항목들의 노동 시간과 비용을 계산합니다.
        """
        total_time = 0.0
        total_cost = 0.0

        for item in items:
            # 노동 시간을 기준으로 비용 산출 (Chaos 측정)
            labor_hours = item.labor_hours
            item_cost = labor_hours * rate_per_hour
            total_time += labor_hours
            total_cost += item_cost

        result = {
            "total_labor_hours": total_time,
            "total_cost": total_cost,
            "items_processed": len(items),
            "average_rate": rate_per_hour
        }
        return result

    def generate_kpi_report(self) -> List[Dict[str, Any]]:
        """
        추적된 비용 항목들을 기반으로 KPI 보고서의 초안을 생성합니다.
        혼돈 vs. 질서 대비 원칙에 따라 핵심 지표를 도출합니다.
        """
        report_data = []
        for item in self.cost_items:
            # 리스크 및 효율성 기반 KPI 정의 (Order 추구)
            risk_score = item.risk_level  # CostItem에서 가져옴
            efficiency = item.efficiency # CostItem에서 가져옴

            # 단순화된 혼돈->질서 변환 로직 적용 예시
            if risk_score > 7:
                status = "High Risk (Chaos)"
            elif efficiency < 0.5:
                status = "Low Efficiency (Chaos)"
            else:
                status = "Stable (Order)"

            report = {
                "item_id": item.item_id,
                "description": item.description,
                "labor_hours": item.labor_hours,
                "calculated_cost": item.labor_hours * 5000, # 임의의 단가 적용 예시
                "risk_status": status,
                "efficiency_score": efficiency,
                "timestamp": datetime.datetime.now().isoformat()
            }
            report_data.append(report)

        return report_data

def run_cost_analysis(cost_items: List[CostItem], kpi_reports: List[KPIReport], hourly_rate: float):
    """
    전체 비용 추적 및 KPI 보고서 생성을 실행하는 메인 함수.
    """
    tracker = CostTracker(cost_items, kpi_reports)

    # 1. 노동 비용 계산 (Chaos 측정)
    labor_summary = tracker.calculate_labor_cost(cost_items, hourly_rate)
    print("\n--- 노동 비용 요약 (Chaos 측면) ---")
    print(f"총 투입 노동 시간: {labor_summary['total_labor_hours']:.2f} 시간")
    print(f"총 추정 비용: {labor_summary['total_cost']:.2f} 원 (시급 {hourly_rate}원 기준)")

    # 2. KPI 보고서 생성 (Order 도출)
    kpi_results = tracker.generate_kpi_report()
    print("\n--- 핵심 KPI 보고서 (Order 도출) ---")
    for report in kpi_results:
        print(f"ID: {report['item_id']} | 상태: {report['risk_status']} | 효율성: {report['efficiency_score']:.2f} | 비용: {report['calculated_cost']:.2f} 원")

    return labor_summary, kpi_results

if __name__ == '__main__':
    # 테스트 데이터 로드 (실제 환경에서는 DB/파일에서 로드될 예정)
    # 임시 더미 데이터 생성
    dummy_cost_items = [
        CostItem(item_id="C001", description="상품 A 발주 및 검수", labor_hours=15.5, risk_level=8, efficiency=0.6),
        CostItem(item_id="C002", description="CS 응대 및 배송 관리", labor_hours=40.0, risk_level=3, efficiency=0.9),
        CostItem(item_id="C003", description="재고 분석 및 예측 모델링", labor_hours=25.0, risk_level=9, efficiency=0.4),
    ]
    dummy_kpi_reports = [KPIReport(report_id="R001", metric="Total Labor Cost", value=11875.0)]

    # 시급 설정 (예시: 5000원)
    HOURLY_RATE = 5000.0

    print("--- 시스템 테스트 시작 ---")
    run_cost_analysis(dummy_cost_items, dummy_kpi_reports, HOURLY_RATE)
    print("\n--- 시스템 테스트 완료 ---")