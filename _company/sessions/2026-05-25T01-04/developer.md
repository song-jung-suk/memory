# 💻 코다리 — Designer가 제작할 썸네일 비주얼 에셋의 제작 과정이 CostItem/KPIReport 시스템과 정확히 연동되도록 필요한 데이터 변환 로직 및 API 통합 가능성을 최종 점검하고, 시각적 에셋 제작에 필요한 최소한의 기술적 요구사항을 보고하라.

💻 코다리: 작업 시작합니다.

CEO의 지시를 확인했습니다. 썸네일 비주얼 에셋 제작 과정이 백엔드 `CostItem/KPIReport` 시스템과 정확히 연동되도록 필요한 데이터 변환 로직 및 API 통합 가능성에 대한 기술적 요구사항을 보고하겠습니다. 시각적 충돌(Chaos)과 질서(Order)의 원칙을 데이터 흐름에 적용하는 것이 핵심입니다.

### 📊 기술 연동 점검 보고: 시각 에셋과 KPI 시스템 통합

**목표:** `CostItem/KPIReport` 데이터를 기반으로 유튜브 쇼츠 썸네일 비주얼 에셋 제작 프로세스를 자동화하고, 시각적 충돌(Chaos)을 극대화하여 전환율(Order)을 높이는 최소한의 기술 스펙 정의.

#### 1. 데이터 변환 로직 (Data Transformation Logic)

비주얼 에셋은 단순한 이미지 배치가 아니라, **KPI 상태를 반영하는 추상적인 시각적 메타포**여야 합니다. 따라서 숫자 데이터를 직접적으로 출력하는 것이 아니라, 시스템이 정의한 'Chaos $\rightarrow$ Order' 매트릭스를 기준으로 색상 팔레트와 레이아웃을 결정해야 합니다.

*   **입력 데이터:** `KPIReport` 및 개별 `CostItem` 데이터 (노동 시간, 리스크 지표, 비용 추이).
*   **변환 로직 (`Transformation Function`):**
    1.  **Chaos Score 계산:** 특정 KPI(예: 배송비 불투명성 지수)를 정규화하여 0~100 사이의 '혼돈 점수'를 산출합니다. 이 점수는 시각적 **Red(Chaos)** 요소의 강도를 결정합니다.
    2.  **Order Score 계산:** 시스템 도입/자동화 수준을 측정하여 0~100 사이의 '질서 점수'를 산출합니다. 이 점수는 시각적 **Blue(Order)** 요소의 지배력을 결정합니다.
    3.  **Color Mapping:** `Chaos Score`에 비례하여 주 색상(Red)의 채도나 명도를 조절하고, `Order Score`에 비례하여 보조 색상(Blue)의 대비를 설정합니다. (예: Chaos가 높을수록 Red 영역이 지배적).
    4.  **Layout Mapping:** 두 점수(`Chaos`, `Order`)의 상대적 비율에 따라 썸네일 내의 분할선 위치, 텍스트 배치 우선순위(문제 제시 vs. 해결책 제시)를 결정합니다.

#### 2. API 통합 가능성 (API Integration Feasibility)

현재 Python/TypeScript 백엔드 시스템과 외부 비주얼 에셋 생성 도구 간의 연결은 **중간 레이어(API Gateway)**를 통해 구현하는 것이 가장 안전하고 확장성이 높습니다.

*   **필요한 API 엔드포인트:**
    *   `/api/visuals/generate?kpi_id={ID}&theme=chaos_order`
        *   이 엔드포인트는 백엔드의 KPI 데이터를 받아, 1단계에서 정의된 변환 로직을 실행하여 **JSON 형식의 시각적 파라미터**를 반환해야 합니다. (예: `{"color_red": "#FF4500", "color_blue": "#1E90FF", "layout_split": "60/40"}`).
*   **통합 방식:**
    *   **Backend (Python/TS):** KPI 데이터를 계산하고, 이 결과를 API를 통해 시각 에셋 생성 모듈에 전달하는 역할을 수행합니다.
    *   **Frontend/Visual Tool:** 외부 툴(혹은 자체 개발된 스크립트)이 이 API를 호출하여 필요한 색상 코드와 레이아웃 정보를 받아 최종 이미지를 렌더링합니다.

#### 3. 최소한의 기술적 요구사항 (Minimum Technical Requirements)

최소한으로 구현되어야 할 것은 **데이터 연동을 위한 인터페이스 정의**입니다.

1.  **모델 확장:** `models.py` 또는 관련 데이터 스키마에 시각화 파라미터(`chaos_score`, `order_score`, `color_map`)를 저장할 필드를 추가해야 합니다.
2.  **API 명세:** 위에서 정의한 `/api/visuals/generate` 엔드포인트의 입력 및 출력 명세를 확정해야 합니다.
3.  **Scripting Layer:** KPI 데이터가 업데이트될 때, 해당 데이터를 읽어와서 **변환 로직을 실행하고 API를 호출하는 스크립트**(`data_to_visual_pipeline.py` 등)를 구축해야 합니다. 이 스크립트는 `cost_tracker.py`의 결과를 참조하도록 설계되어야 합니다.

**결론:** 시각 에셋 제작은 **데이터 기반 자동화 파이프라인(Data-to-Visual Transformation Pipeline)**을 통해 구현 가능하며, 이는 백엔드 로직(`cost_tracker.py`)과 프레젠테이션 레이어 사이에 명확한 API 통로를 설치함으로써 달성할 수 있습니다.

📊 평가: 진행중 — 기술적 요구사항은 정의되었으나, 실제 데이터 변환 스크립트 및 API 구현 단계가 필요함
📝 다음 단계: `data_to_visual_pipeline.py`의 초기 스켈레톤을 작성하여 KPI 데이터를 시각 파라미터로 변환하는 로직을 설계하겠습니다.
