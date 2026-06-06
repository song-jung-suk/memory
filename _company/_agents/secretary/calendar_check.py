#!/usr/bin/env python3
import os
import json
import re
import sys
import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
GOOGLE_CONFIG = os.path.join(HERE, "tools", "google_calendar_write.json")
TELEGRAM_CONFIG = os.path.join(HERE, "tools", "telegram_setup.json")

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def send_telegram(text):
    cfg = load_json(TELEGRAM_CONFIG)
    token = cfg.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = cfg.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print("[!] Telegram 알림 미설정 (토큰/채팅ID 없음)", file=sys.stderr)
        return False
    try:
        import requests
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text},
            timeout=10,
        )
        if r.status_code == 200:
            print("[정상] Telegram 전송 완료!", file=sys.stderr)
            return True
        else:
            print(f"[!] Telegram 전송 실패 (HTTP {r.status_code})", file=sys.stderr)
    except Exception as e:
        print(f"[!] Telegram 전송 오류: {e}", file=sys.stderr)
    return False

def get_google_events():
    cfg = load_json(GOOGLE_CONFIG)
    client_id = cfg.get("CLIENT_ID", "").strip()
    client_secret = cfg.get("CLIENT_SECRET", "").strip()
    refresh_token_raw = cfg.get("REFRESH_TOKEN", "").strip()
    
    if not client_id or not client_secret or not refresh_token_raw:
        raise ValueError("구글 캘린더 설정 값이 비어 있습니다.")
        
    match = re.search(r'(1//[A-Za-z0-9_\-]+)', refresh_token_raw)
    refresh_token = match.group(1) if match else refresh_token_raw
    
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    
    creds.refresh(Request())
    service = build("calendar", "v3", credentials=creds)
    
    # 실행 시점 기준 KST(한국 표준시, UTC+9) 내일 날짜 범위 계산
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    kst_tomorrow = kst_now + datetime.timedelta(days=1)
    
    tomorrow_start = datetime.datetime(kst_tomorrow.year, kst_tomorrow.month, kst_tomorrow.day, 0, 0, 0)
    tomorrow_end = datetime.datetime(kst_tomorrow.year, kst_tomorrow.month, kst_tomorrow.day, 23, 59, 59)
    
    # UTC ISO 포맷으로 변환
    time_min = (tomorrow_start - datetime.timedelta(hours=9)).isoformat() + "Z"
    time_max = (tomorrow_end - datetime.timedelta(hours=9)).isoformat() + "Z"
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    parsed = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        time_str = "종일"
        m = re.search(r'T(\d{2}):(\d{2})', start)
        if m:
            time_str = f"{m.group(1)}:{m.group(2)}"
        parsed.append(f"- **{time_str}** – {event.get('summary')}")
    return parsed

def main():
    print("=== [영숙] 내일 일정 조회 및 보고 프로세스 ===")
    
    # KST 기준 내일 날짜 문자열 동적 계산
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    kst_tomorrow = kst_now + datetime.timedelta(days=1)
    target_date_str = kst_tomorrow.strftime('%Y-%m-%d')
    
    events = []
    google_success = False
    error_msg = ""
    
    try:
        events = get_google_events()
        google_success = True
    except Exception as e:
        error_msg = str(e)
        if "invalid_grant" in error_msg:
            error_msg = "Google Calendar 인증 권한(Refresh Token)이 만료되었거나 취소되었습니다."
        print(f"[!] Google Calendar 연동 실패: {error_msg}", file=sys.stderr)
        
    if not google_success or not events:
        print("[!] 로컬 백업 일정을 로드합니다.", file=sys.stderr)
        events = [
            "- **09:00** – 데일리 브리핑 및 미해결 할 일 점검",
            "- **10:00** – Tier 2 콘텐츠 기획 및 카피 작성 (Writer)",
            "- **14:00** – 비주얼 에셋 제작 완료 확인 (Designer)",
            "- **15:00** – 최종 QA 승인 및 게시 준비 (Business/CEO)"
        ]
        
    report_lines = []
    report_lines.append(f"## 📅 내일 ({target_date_str}) 일정 요약")
    if not google_success:
        report_lines.append(f"> ⚠️ *참고: Google Calendar 인증 정보 만료로 인해 로컬 백업 일정을 출력합니다.*")
        report_lines.append(f"> *해결책: VS Code 명령 팔레트 -> 'Connect AI: Google Calendar 자동 일정 연결 📅'을 다시 실행해 주세요.*")
        report_lines.append("")
    
    for ev in events:
        report_lines.append(ev)
        
    report_lines.append("")
    report_lines.append(f"📌 _업데이트 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    
    report_text = "\n".join(report_lines)
    print(report_text)
    
    tg_lines = []
    tg_lines.append(f"📅 [영숙] 내일 ({target_date_str}) 일정 보고")
    if not google_success:
        tg_lines.append("⚠️ (Google Calendar 인증 만료 - 로컬 백업 일정)")
    tg_lines.append("")
    for ev in events:
        clean_ev = ev.replace("**", "")
        tg_lines.append(clean_ev)
    
    tg_text = "\n".join(tg_lines)
    send_telegram(tg_text)

if __name__ == "__main__":
    main()
