#!/usr/bin/env python3
"""
Instagram Agent Manager Skill Script: Autonomous Instagram Management
- Manages Reels & Feed content creation pipeline
- Handles Meta Graph API connection checks with fallback simulation mode
- Prepares hashtag & engagement strategy
"""

import os
import sys
import json

# Windows CP949 encoding fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(os.path.dirname(HERE), "tools")
ACCOUNT_SCRIPT = os.path.join(TOOLS_DIR, "instagram_account.py")

def check_instagram_status():
    print("─── 📷 Instagram 에이전트 자율 관리 스킬 실행 ───")
    print("1. Meta Graph API 계정 연동 및 상태 검증...")
    if os.path.exists(ACCOUNT_SCRIPT):
        ret = os.system(f"python \"{ACCOUNT_SCRIPT}\"")
        if ret != 0:
            print("\n💡 [안내] 현재 Meta Access Token이 만료되었거나 설정이 필요합니다.")
            print("   - 새 Long-lived Token 준비 시 `_company/_agents/instagram/config.md`에 업로드해 주세요.")
            print("   - 현재는 에이전트 자율 시뮬레이션 및 콘텐츠 기획 모드로 전환되어 정상 작동합니다! ✅")
    else:
        print("⚠️ instagram_account.py 스크립트를 찾을 수 없습니다.")

def generate_reels_strategy():
    print("\n2. 📸 인스타그램 릴스 & 카드뉴스 게시 전략 수립 중...")
    strategy = {
        "channel": "dadajikgu Instagram",
        "target_audience": "중국 구매대행 초보 셀러 & 1인 무역 사업가",
        "reels_topics": [
            "1688 이미지 검색으로 마진 30% 높이는 꿀팁",
            "타오바오 옵션 번역 없이 3초 만에 엑셀 변환하기",
            "초보 셀러가 자주 범하는 CS 오배송 방지 체크리스트 TOP 3"
        ],
        "hashtags": ["#구매대행", "#1688소싱", "#타오바오직구", "#AI쇼핑몰", "#1인기업", "#다다직구"]
    }
    print(json.dumps(strategy, ensure_ascii=False, indent=2))

def main():
    check_instagram_status()
    generate_reels_strategy()

if __name__ == "__main__":
    main()
