#!/usr/bin/env python3
"""Instagram Account / Connection - shared config and verification.

This script loads settings from instagram_account.json (or config.md) and
performs a verification request to Meta Graph API to check connection.
"""
import os, json, sys, re
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "instagram_account.json")
CONFIG_MD_PATH = os.path.join(os.path.dirname(HERE), "config.md")

def load_config():
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass

    token = (cfg.get("META_ACCESS_TOKEN") or "").strip()
    business_id = (cfg.get("INSTAGRAM_BUSINESS_ID") or "").strip()

    if not token or not business_id:
        if os.path.exists(CONFIG_MD_PATH):
            try:
                with open(CONFIG_MD_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                m_token = re.search(r"META_ACCESS_TOKEN\s*[:：=]\s*([A-Za-z0-9_\-]+)", content)
                m_id = re.search(r"INSTAGRAM_BUSINESS_ID\s*[:：=]\s*([A-Za-z0-9_\-]+)", content)
                if m_token and not token:
                    token = m_token.group(1).strip()
                if m_id and not business_id:
                    business_id = m_id.group(1).strip()
            except Exception:
                pass

    return {
        "META_ACCESS_TOKEN": token,
        "INSTAGRAM_BUSINESS_ID": business_id,
        "TELEGRAM_BOT_TOKEN": (cfg.get("TELEGRAM_BOT_TOKEN") or "").strip(),
        "TELEGRAM_CHAT_ID": (cfg.get("TELEGRAM_CHAT_ID") or "").strip(),
    }

def main():
    cfg = load_config()
    token = cfg.get("META_ACCESS_TOKEN")
    business_id = cfg.get("INSTAGRAM_BUSINESS_ID")

    masked_token = (token[:8] + "…" + token[-8:]) if len(token) >= 16 else ("(빈 값)" if not token else "(짧음)")
    masked_id = (business_id[:4] + "…" + business_id[-4:]) if len(business_id) >= 8 else ("(빈 값)" if not business_id else business_id)

    print("─── Instagram 계정 연동 상태 ───")
    print(f"  Business ID  : {masked_id}")
    print(f"  Access Token : {masked_token}")
    print(f"  Telegram Bot : {'설정됨' if cfg.get('TELEGRAM_BOT_TOKEN') else '(없음)'}")
    print()

    if not token or not business_id:
        print("⚠️ Meta Access Token 또는 Instagram Business Account ID가 비어있어요.")
        print("   설정창(⚙️) 또는 config.md 파일을 확인해 주세요.")
        sys.exit(1)

    print("🔌 Meta Graph API 연결 테스트 중...")
    version = "v23.0"
    url = f"https://graph.instagram.com/{version}/{business_id}"
    try:
        r = requests.get(url, params={
            "fields": "username,name,biography",
            "access_token": token
        }, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            print("✅ 연결 성공!")
            print(f"  계정명 (Username) : @{data.get('username', 'N/A')}")
            print(f"  이름 (Name)       : {data.get('name', 'N/A')}")
            print(f"  소개 (Biography)  : {data.get('biography', 'N/A')}")
        else:
            print(f"❌ 연결 실패 (HTTP {r.status_code})")
            print(f"  오류 내용: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
