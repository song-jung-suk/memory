import os
import re
import json
import urllib.request
import urllib.parse
import sys
import io

# Windows 콘솔 인코딩 방지
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SECRETARY_CONFIG_PATH = r"E:\work\_company\_agents\secretary\config.md"
DEVELOPER_CONFIG_PATH = r"E:\work\_company\_agents\developer\config.md"

def load_markdown_config(config_path):
    config = {}
    if not os.path.exists(config_path):
        return config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = r"-\s*([A-Z_]+)\s*:\s*[\"']?(.*?)[\"']?\s*$"
        matches = re.findall(pattern, content, re.MULTILINE)
        for key, val in matches:
            config[key] = val.strip().strip('"').strip("'")
    except Exception as e:
        print(f"⚠️ 설정 파일 로드 에러 ({config_path}): {e}")
    return config

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ 텔레그램 메시지 전송 실패: {e}")
        return None

def send_email_report(sender_email, app_password, receiver_email, subject, body_markdown):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    if not sender_email or not app_password or not receiver_email:
        print("⚠️ 이메일 계정 설정(SENDER_EMAIL / SENDER_APP_PASSWORD)이 누락되었습니다.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Connect AI 비서실장 <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        # 마크다운을 간단한 HTML 스타일로 변환
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 700px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{subject}</h2>
                <div style="white-space: pre-wrap; background-color: #f9f9f9; padding: 15px; border-radius: 5px; font-size: 14px;">{body_markdown}</div>
                <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;" />
                <p style="font-size: 12px; color: #777;">본 메일은 Connect AI 비서실장 에이전트 시스템에 의해 자동 발송되었습니다.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print(f"📧 이메일 보고서 발송 완료! ({receiver_email})")
        return True
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        return False

def generate_affiliate_content(item_keyword, gemini_api_key):
    prompt = f"""당신은 국내 최정상 커머스 마케터이자 AI 콘텐츠 크리에이터입니다.
대상 상품/키워드: '{item_keyword}' (쿠팡 파트너스 및 알리익스프레스 직구 아이템)

아래 3가지 채널용 마케팅 원고를 한 번에 작성해 주세요.

1. 🎬 [쇼츠/틱톡 숏폼 스크립트] (15초분량)
- 3초 훅 (시청자 주의 유도)
- 본문 혜택 (핵심 셀링 포인트 2가지)
- CTA (고정 댓글 링크 클릭 유도)

2. 📸 [인스타그램 피드/카드뉴스 원고]
- 카드뉴스 3장 요약 텍스트
- 게시글 본문 캡션 + 추천 해시태그 5개
- 댓글 유도 문구 ("댓글에 '링크' 남겨주시면 주소 쏴드립니다!")

3. 📝 [네이버 블로그 SEO 최적화 리뷰 원고]
- 제목 (검색 노출 최적화)
- 본문 (특장점, 실제 사용 팁, 가성비 비교)
- 구매 버튼 및 파트너스 대가성 문구 ("이 포스팅은 쿠팡 파트너스/알리 어필리에이트 활동의 일환으로 일정액의 수수료를 제공받습니다.")

응답은 마크다운 형식으로 명확히 구분해서 작성해 주세요. 장황한 인삿말은 생략하세요."""

    # 1. [우선순위 1] 설치된 로컬 LLM (LM Studio 1234 또는 Ollama 11434 - Qwen 3.5 4B 등) 연결 시도
    local_urls = [
        ("http://127.0.0.1:1234/v1/chat/completions", "LM Studio"),
        ("http://127.0.0.1:11434/api/generate", "Ollama")
    ]

    # LM Studio 시도
    try:
        payload = {
            "model": "qwen3.5",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        req = urllib.request.Request(
            local_urls[0][0],
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=40) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            text = res_data['choices'][0]['message']['content'].strip()
            print("🧠 [무료 로컬 LLM (LM Studio / Qwen 3.5) 생성 성공]")
            return text
    except Exception:
        pass

    # Ollama 시도
    try:
        payload = {
            "model": "qwen",
            "prompt": prompt,
            "stream": False
        }
        req = urllib.request.Request(
            local_urls[1][0],
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=40) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            text = res_data['response'].strip()
            print("🧠 [무료 로컬 LLM (Ollama / Qwen) 생성 성공]")
            return text
    except Exception:
        pass

    # 2. [우선순위 2 - 백업] 로컬 LLM이 꺼져있을 때만 구글 Gemini API 활용
    if gemini_api_key:
        print("🌐 [로컬 LLM 미연결 -> 구글 Gemini API 백업 사용]")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                text = res_data['candidates'][0]['content']['parts'][0]['text']
                return text
        except Exception as e:
            print(f"❌ Gemini API 생성 실패: {e}")

    return None

def main():
    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:])
    else:
        keyword = "가성비 알리 꿀템 / 1688 소싱 추천 아이템"

    sec_cfg = load_markdown_config(SECRETARY_CONFIG_PATH)
    dev_cfg = load_markdown_config(DEVELOPER_CONFIG_PATH)

    token = sec_cfg.get("TELEGRAM_BOT_TOKEN")
    chat_id = sec_cfg.get("TELEGRAM_CHAT_ID")
    gemini_key = dev_cfg.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not token or not chat_id:
        print("❌ 텔레그램 토큰/채팅ID가 필요합니다.")
        sys.exit(1)

    print(f"🚀 어필리에이트 3-트랙 콘텐츠 생성 중: {keyword}")
    
    if not gemini_key:
        content = f"""🛍️ <b>[어필리에이트 3-트랙 추천 원고 예시]</b>
<b>키워드:</b> {keyword}

<b>1. 🎬 숏폼 스크립트 (15초)</b>
- [0-3초] "아직도 타오바오에서 이 가격 주고 사세요?"
- [3-12초] "1688 직구 가성비 꿀템 TOP 3! 성능은 똑같은데 가격은 1/3입니다."
- [12-15초] "구매 링크는 아래 고정 댓글 확인해 주세요!"

<b>2. 📸 인스타그램 카드뉴스</b>
- 슬라이드 1: 소싱 셀러 필수 직구 아이템
- 슬라이드 2: 가성비 비교 & 마진 계산
- 슬라이드 3: 구매처 링크 안내

<b>3. 📝 네이버 블로그 포스팅</b>
- 제목: [1688/알리] 직구 셀러 추천 필수 아이템 솔직 후기
- 본문: 제품 특장점 정리 및 추천 대상 안내
- 대가성 문구: (쿠팡 파트너스/알리 어필리에이트 활동으로 수수료를 제공받을 수 있습니다.)"""
    else:
        generated = generate_affiliate_content(keyword, gemini_key)
        if generated:
            content = f"🛍️ <b>[쿠팡/알리 어필리에이트 3-트랙 마케팅 원고]</b>\n<b>대상:</b> {keyword}\n\n" + generated
        else:
            content = f"❌ {keyword} 원고 생성 실패."

    sender_email = dev_cfg.get("SENDER_EMAIL")
    app_password = dev_cfg.get("SENDER_APP_PASSWORD")
    receiver_email = dev_cfg.get("RECEIVER_EMAIL")

    subject = f"🛍️ [Connect AI] 어필리에이트 3-트랙 마케팅 원고 보고서 ({keyword})"
    send_email_report(sender_email, app_password, receiver_email, subject, content)
    
    # 텔레그램으로도 수신 요약 알림 전송 (선택 사항)
    if token and chat_id:
        send_telegram_message(token, chat_id, f"📧 <b>'{keyword}' 어필리에이트 마케팅 원고가 이메일({receiver_email})로 전송되었습니다.</b>\n수신함을 확인해 보세요!")

    print(f"✅ 이메일({receiver_email})로 어필리에이트 3-트랙 원고 전송 완료!")

if __name__ == "__main__":
    main()
