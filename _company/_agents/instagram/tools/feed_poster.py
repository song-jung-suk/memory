#!/usr/bin/env python3
"""Instagram Feed Poster - Uploads local images to catbox.moe and publishes them on Instagram.
"""
import os, sys, json, time, re
import argparse
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "feed_poster.json")

# Import the loader function from instagram_account.py to reuse credentials
try:
    from instagram_account import load_config as load_account_config
except ImportError:
    # Fallback loader logic if import fails
    def load_account_config():
        return {
            "META_ACCESS_TOKEN": "",
            "INSTAGRAM_BUSINESS_ID": "",
            "TELEGRAM_BOT_TOKEN": "",
            "TELEGRAM_CHAT_ID": ""
        }

def load_poster_config():
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    return {
        "IMAGE_PATH": (cfg.get("IMAGE_PATH") or "").strip(),
        "CAPTION": (cfg.get("CAPTION") or "").strip(),
        "PREVIEW": bool(cfg.get("PREVIEW")),
        "TELEGRAM_NOTIFY": bool(cfg.get("TELEGRAM_NOTIFY", True)),
    }

def resolve_telegram():
    # 1. Check secretary config.md
    token, chat = "", ""
    brain_root = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    sec_config_md = os.path.join(brain_root, "_agents", "secretary", "config.md")
    sec_json = os.path.join(brain_root, "_agents", "secretary", "tools", "telegram_setup.json")
    
    # Check JSON first
    if os.path.exists(sec_json):
        try:
            with open(sec_json, "r", encoding="utf-8") as f:
                s_cfg = json.load(f)
            token = (s_cfg.get("TELEGRAM_BOT_TOKEN") or "").strip()
            chat = (s_cfg.get("TELEGRAM_CHAT_ID") or "").strip()
        except Exception:
            pass

    # Fallback to config.md
    if not token or not chat:
        if os.path.exists(sec_config_md):
            try:
                with open(sec_config_md, "r", encoding="utf-8") as f:
                    content = f.read()
                m_token = re.search(r"TELEGRAM_BOT_TOKEN\s*[:：=]\s*([A-Za-z0-9:_\-]+)", content)
                m_chat = re.search(r"TELEGRAM_CHAT_ID\s*[:：=]\s*(-?\d+)", content)
                if m_token: token = m_token.group(1).strip()
                if m_chat: chat = m_chat.group(1).strip()
            except Exception:
                pass
                
    return token, chat

def send_telegram_notification(token, chat, text):
    if not token or not chat:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
            timeout=15
        )
    except Exception as e:
        print(f"⚠️ 텔레그램 알림 전송 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description="Instagram Feed Poster Tool")
    parser.add_argument("--preview", action="store_true", help="Run in preview simulation mode")
    parser.add_argument("--image", type=str, help="Override image path")
    parser.add_argument("--caption", type=str, help="Override caption")
    args = parser.parse_args()

    # Load configurations
    acct = load_account_config()
    post = load_poster_config()

    # Apply overrides
    image_path = args.image if args.image else post["IMAGE_PATH"]
    caption = args.caption if args.caption else post["CAPTION"]
    preview = args.preview or post["PREVIEW"]
    
    token = acct["META_ACCESS_TOKEN"]
    business_id = acct["INSTAGRAM_BUSINESS_ID"]

    print("─── Instagram 자동 업로드 도구 ───")
    print(f"  이미지 경로: {image_path or '(지정되지 않음)'}")
    print(f"  캡션 길이  : {len(caption)}자")
    print(f"  미리보기   : {'활성화 (업로드 없음)' if preview else '비활성화 (실제 게시)'}")
    print()

    # Check basic inputs
    if not image_path:
        print("❌ 오류: 업로드할 이미지 경로가 지정되지 않았습니다.")
        sys.exit(1)
        
    if not os.path.exists(image_path):
        print(f"❌ 오류: 이미지 파일을 찾을 수 없습니다: {image_path}")
        sys.exit(1)

    tg_token, tg_chat = resolve_telegram()

    if preview:
        print("=== [미리보기 시뮬레이션] ===")
        print("1. 이미지 임시 업로드 시뮬레이션 (catbox.moe)")
        print("2. Instagram 미디어 컨테이너 생성 시뮬레이션 (v23.0 API)")
        print("3. 대기 후 퍼블리시 발행 시뮬레이션")
        print("\n[캡션 내용]")
        print(caption)
        print("\n✅ 시뮬레이션 완료. 실제 업로드하려면 설정을 변경해 주세요.")
        
        if post["TELEGRAM_NOTIFY"] and tg_token and tg_chat:
            msg = f"👁️ *Instagram 업로드 시뮬레이션 완료*\n- 이미지: `{os.path.basename(image_path)}`\n- 결과: 정상 동작 시뮬레이션 완료"
            send_telegram_notification(tg_token, tg_chat, msg)
        return

    if not token or not business_id:
        print("❌ 오류: 계정 연동 설정이 불완전합니다. instagram_account 도구를 실행하여 연동해 주세요.")
        sys.exit(1)

    print("Step 1. 이미지를 공개 서버에 임시 업로드합니다 (catbox.moe)...")
    public_url = ""
    try:
        with open(image_path, "rb") as f:
            files = {
                "reqtype": (None, "fileupload"),
                "fileToUpload": (os.path.basename(image_path), f, "image/png"),
            }
            res = requests.post("https://catbox.moe/user/api.php", files=files)
            res.raise_for_status()
            public_url = res.text.strip()
            print(f"  공개 URL 획득 완료: {public_url}")
    except Exception as e:
        err_msg = f"❌ 이미지 서버 업로드 실패: {e}"
        print(err_msg)
        if post["TELEGRAM_NOTIFY"]:
            send_telegram_notification(tg_token, tg_chat, f"🚨 *Instagram 업로드 에러*\n- 이미지: `{os.path.basename(image_path)}`\n- 에러: 이미지 임시 업로드 중 오류 발생\n`{e}`")
        sys.exit(1)

    print("Step 2. Meta Graph API를 사용하여 미디어 컨테이너를 생성합니다...")
    version = "v23.0"
    base_url = f"https://graph.instagram.com/{version}/{business_id}"
    creation_id = ""
    try:
        r = requests.post(f"{base_url}/media", data={
            "image_url": public_url,
            "caption": caption,
            "access_token": token
        }, timeout=30)
        res_data = r.json()
        creation_id = res_data.get("id")
        
        if not creation_id:
            raise ValueError(f"ID를 얻지 못했습니다. API 응답: {res_data}")
        print(f"  컨테이너 생성 완료! (ID: {creation_id})")
    except Exception as e:
        err_msg = f"❌ Instagram 컨테이너 생성 오류: {e}"
        print(err_msg)
        if post["TELEGRAM_NOTIFY"]:
            send_telegram_notification(tg_token, tg_chat, f"🚨 *Instagram 업로드 에러*\n- 이미지: `{os.path.basename(image_path)}`\n- 에러: 미디어 컨테이너 생성 실패\n`{e}`")
        sys.exit(1)

    print("Step 3. Instagram 서버 미디어 처리를 대기합니다 (30초)...")
    time.sleep(30)

    print("Step 4. 미디어를 최종 발행합니다...")
    try:
        r_pub = requests.post(f"{base_url}/media_publish", data={
            "creation_id": creation_id,
            "access_token": token
        }, timeout=30)
        res_pub = r_pub.json()
        post_id = res_pub.get("id")
        
        if not post_id:
            raise ValueError(f"발행 실패. API 응답: {res_pub}")
            
        success_msg = f"🌟 Instagram 피드 게시 성공! (Post ID: {post_id})"
        print(success_msg)
        
        # Log to activity log
        log_file = os.path.join(os.path.dirname(HERE), "activity.log")
        try:
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pushed Instagram post {post_id} with image {os.path.basename(image_path)}\n")
        except Exception:
            pass

        if post["TELEGRAM_NOTIFY"]:
            send_telegram_notification(
                tg_token,
                tg_chat,
                f"✅ *Instagram 게시 성공!*\n- 이미지: `{os.path.basename(image_path)}`\n- 포스트 ID: `{post_id}`\n- 내용: {caption[:50]}..."
            )
            
    except Exception as e:
        err_msg = f"❌ Instagram 최종 발행 오류: {e}"
        print(err_msg)
        if post["TELEGRAM_NOTIFY"]:
            send_telegram_notification(tg_token, tg_chat, f"🚨 *Instagram 발행 에러*\n- 이미지: `{os.path.basename(image_path)}`\n- 에러: 최종 발행(Publish) 중 실패\n`{e}`")
        sys.exit(1)

if __name__ == "__main__":
    main()
