#!/usr/bin/env python3
"""
Secretary Yeongsook Skill: Daily Email Summarizer & Telegram Alert
- Fetches recent important emails (IMAP / Gmail API simulation or local mailbox)
- Uses local LLM (Ollama or local fallback transformer) to summarize email content securely without privacy leaks
- Sends the daily email summary to CEO via Telegram Bot
"""

import os
import sys
import json
import requests
from datetime import datetime

# Windows CP949 encoding fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "telegram_setup.json")

def load_telegram_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def fetch_daily_emails():
    """Simulates/Fetches important emails from mailbox for daily briefing."""
    # Sample structure representing fetched emails
    return [
        {
            "sender": "partner@taobao-sourcing.com",
            "subject": "[중요] 1688 대형 사입 단가 네고 승인 건 및 배대지 일정 안내",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "body": "안녕하세요 송요셉 대표님, 요청해주신 의류 및 전자제품 1688 사입 건 수량별 12% 단가 인하가 최종 승인되었습니다. 출고는 이번 주 목요일 진행될 예정입니다."
        },
        {
            "sender": "notice@google.com",
            "subject": "Google Workspace 계정 보안 및 캘린더 연동 알림",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "body": "Google Calendar API 연동이 정상적으로 유지되고 있습니다. 주요 대표님 일정이 자동으로 동기화됩니다."
        }
    ]

def summarize_with_local_llm(emails):
    """Uses Ollama (local LLM) to summarize email text securely."""
    ollama_url = "http://localhost:11434/api/generate"
    summary_results = []

    for idx, mail in enumerate(emails, 1):
        prompt = f"""다음 이메일 내용을 대표님께 보고할 수 있도록 핵심만 2줄로 명확히 한국어로 요약해줘:
발신자: {mail['sender']}
제목: {mail['subject']}
본문: {mail['body']}
"""
        summarized_text = ""
        try:
            r = requests.post(ollama_url, json={
                "model": "qwen2.5:latest", # or llama3/mistral local model
                "prompt": prompt,
                "stream": False
            }, timeout=5)
            if r.status_code == 200:
                summarized_text = r.json().get("response", "").strip()
        except Exception:
            # Fallback to local rule-based summarizer if Ollama service is offline
            summarized_text = f"• {mail['subject']}\n  - 주요내용: {mail['body'][:80]}..."

        summary_results.append(f"📧 [{idx}] {mail['subject']}\n발신: {mail['sender']}\n요약:\n{summarized_text}\n")

    return "\n".join(summary_results)

def send_telegram_report(text):
    cfg = load_telegram_config()
    token = cfg.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = cfg.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ 텔레그램 토큰 또는 Chat ID가 설정되지 않았습니다. 콘솔 출력으로 대체합니다.")
        print(text)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"📱 *[영숙 비서실장 데일리 이메일 요약 보고]*\n\n{text}",
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ 텔레그램 데일리 이메일 요약 보고 성공!")
            return True
        else:
            print(f"❌ 텔레그램 발송 실패 (HTTP {r.status_code}): {r.text}")
    except Exception as e:
        print(f"❌ 텔레그램 발송 오류: {e}")
    return False

def main():
    print("─── 📱 비서 영숙: 데일리 이메일 요약 & 텔레그램 보고 ───")
    emails = fetch_daily_emails()
    print(f"📥 수신된 주요 이메일 수: {len(emails)}개")
    
    print("🧠 로컬 LLM을 사용하여 이메일 보안 요약 진행 중...")
    summary = summarize_with_local_llm(emails)
    
    print("\n📤 텔레그램 보고서 전송 중...")
    send_telegram_report(summary)

if __name__ == "__main__":
    main()
