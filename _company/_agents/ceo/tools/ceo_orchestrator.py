#!/usr/bin/env python3
"""
CEO Agent Skill Script: Orchestration & Report Aggregator
- Scans team sessions and status
- Generates task assignments for sub-agents
- Aggregates reports into a comprehensive CEO Summary
"""

import os
import json
import sys
from datetime import datetime

# Windows CP949 encoding fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

COMPANY_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SESSIONS_DIR = os.path.join(COMPANY_DIR, "sessions")

def get_latest_session():
    if not os.path.exists(SESSIONS_DIR):
        return None
    sessions = [os.path.join(SESSIONS_DIR, d) for d in os.listdir(SESSIONS_DIR) if os.path.isdir(os.path.join(SESSIONS_DIR, d))]
    if not sessions:
        return None
    sessions.sort(reverse=True)
    return sessions[0]

def orchestrate_tasks():
    """Generates task assignment matrix split into Phase 1 and Phase 2 (max 2 agents per batch)."""
    task_matrix = {
        "timestamp": datetime.now().isoformat(),
        "max_concurrent_agents": 2,
        "phase_1_immediate": [
            {
                "agent": "secretary",
                "role": "비서 영숙",
                "priority": 1,
                "tasks": ["텔레그램 수발신 상태 점검", "구글 캘린더 일정 동기화", "데일리 중요 이메일 로컬 LLM 요약 보고"]
            },
            {
                "agent": "instagram",
                "role": "Head of Instagram",
                "priority": 2,
                "tasks": ["릴스 및 피드 카드 뉴스 기획", "해시태그 및 인게이지먼트 자율 관리", "Meta Graph 연동 검증"]
            }
        ],
        "phase_2_sequential": [
            {
                "agent": "youtube",
                "role": "레오 (Head of YouTube)",
                "priority": 3,
                "tasks": ["쇼츠 트렌드 분석", "영업/마케팅 영상 대본 작성"]
            },
            {
                "agent": "developer",
                "role": "코다리 (시니어 풀스택)",
                "priority": 4,
                "tasks": ["자동화 파이프라인 유지보수", "로컬 LLM 연동 모듈 안정화"]
            },
            {
                "agent": "business",
                "role": "현빈 (비즈니스 전략가)",
                "priority": 5,
                "tasks": ["구매대행 셀러 애로사항 분석", "신규 마케팅 템플릿 기획"]
            }
        ]
    }
    return task_matrix

def summarize_latest_reports():
    latest = get_latest_session()
    if not latest:
        return "최근 진행된 세션 보고서가 없습니다."
    
    report_file = os.path.join(latest, "_report.md")
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"세션 {os.path.basename(latest)} 진행 중..."

def main():
    print("─── 🧭 CEO 에이전트 업무 오케스트레이션 ───")
    matrix = orchestrate_tasks()
    print(json.dumps(matrix, ensure_ascii=False, indent=2))
    
    print("\n─── 📊 최근 통합 보고서 요약 ───")
    summary = summarize_latest_reports()
    print(summary[:500] + ("..." if len(summary) > 500 else ""))

if __name__ == "__main__":
    main()
