# 🎯 채널 KPI 현황 및 주간 목표 설정 (가설 모드)
**작성일**: 2026.08.11  
**상태**: 데이터 수집 대기 중

## 1. 현재 데이터 상태
| 플랫폼 | 데이터 상태 | 장애 원인 | 필요 조치 |
| :--- | :--- | :--- | :--- |
| **YouTube** | ⚠️ 준비 중 | OAuth 연결 부족 | CoDari 에이전트: 설정 가이드 배포 |
| **Instagram** | ❌ 미집계 | API 토큰 누락 | Business + CoDari: 토큰 재발급 요청 |
| **PayPal** | ❌ 실패 | API Key 오류 | CoDari 에이전트: 환경 설정 복원 |

## 2. 가설 기반 주간 목표 (Data-Scarcity Mode)
**목표**: 월 100 만 원 달성 및 데이터 확보 후 KPI 최적화

| 지표 | 현재 목표값 | 근거 (Self-RAG 지식) | 실행 전략 |
| :--- | :--- | :--- | :--- |
| **CTR** | > 8.5% | [근거: sessions/2026-05-09T13-18] 숨겨진 비용 제거 제안서 | Writer + Designer: '배송비 TOP3' 콘텐츠 제작 |
| **AVD (시청 지속률)** | > 70% | [근거: sessions/2026-05-21T02-20] Chaos→Order 프레임워크 | Scripting: Pain Point 강조 후 해결책 제시 |
| **유료 전환** | 100 만 원/월 | B2B AI 도입 제안서 배포 (로컬 무료 모델) | Business: 'Gemma/Qwen 세팅 교육 패키지' 초안 작성 |

## 3. 데이터 수집 완료 시 재평가 지표
- YouTube: `View Duration` > 45% 이상 유지
- PayPal: `Daily Revenue` > $20 이상 달성
- Instagram: `Link Click Rate` > 15% 이상

## 4. 다음 액션 (CoDari 분배)
- **Task 1**: YouTube OAuth 연결 가이드 생성 및 배포 (`youtube_oauth_guide.md`)
- **Task 2**: PayPal API 환경 복원 스크립트 (`paypal_revenue_fix.py`)