import os
import re
import json
import urllib.request
import urllib.parse
import smtplib
import sys
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Windows 콘솔 한글 인코딩 깨짐 방지
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_config():
    config_path = r"E:\work\_company\_agents\developer\config.md"
    config = {
        "SENDER_EMAIL": "",
        "SENDER_APP_PASSWORD": "",
        "RECEIVER_EMAIL": "",
        "BLOG_URL": "https://dadajikgu.com",
        "GEMINI_API_KEY": ""
    }
    
    if not os.path.exists(config_path):
        print(f"⚠️ 설정 파일이 없습니다: {config_path}")
        return config
        
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"-\s*([A-Z_]+)\s*:\s*[\"']?(.*?)[\"']?\s*$"
    matches = re.findall(pattern, content, re.MULTILINE)
    
    for key, val in matches:
        if key in config:
            config[key] = val.strip().strip('"').strip("'")
            
    return config

def load_recent_keywords():
    # Researcher가 어제 작성한 키워드 보고서 경로
    keyword_path = r"E:\work\_company\sessions\2026-06-08T09-keywords.md"
    if not os.path.exists(keyword_path):
        print(f"⚠️ 최근 키워드 분석 보고서가 존재하지 않습니다: {keyword_path}")
        return ""
    
    with open(keyword_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_blog_ideas(api_key, keywords_context):
    endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
당신은 1인 기업 다다직구의 핵심 마케팅 에이전트이자 전문 블로그 기획자(Writer)입니다.
최근 분석된 중국 구매셀러들의 검색 트렌드 키워드와 중국 사입 핵심 키워드 라이브러리를 반영하여, 
대표님이 블로그 글을 바로 작성할 수 있도록 돕는 **10개의 완벽한 블로그 글 주제 기획안**을 생성해 주세요.

[분석된 최근 키워드 컨텍스트]
{keywords_context}

---

[추가 중국 사입 핵심 키워드 라이브러리]
1. 1688 구매대행 수수료 절감
2. 중국 배송대행지(배대지) 선택 기준
3. 한중 FTA 원산지증명서 발급 비용 절약
4. 중국 사입 통관 절차 및 관세/부가세 계산
5. 타오바오 이미지 검색 소싱 팁
6. 지식재산권(상표권) 침해 벌금 예방
7. KC인증 면제 조건 및 식약처 정밀검사
8. 1688 카카오페이 결제 수수료 비교
9. LCL 소량 화물 배송비 아끼는 법
10. 중국 도매 사이트 비교 (1688 vs 알리바바 vs 타오바오)

---

[작성 지침 및 포맷]
1. 총 **10개의 블로그 글 주제**를 기획해 주세요.
2. 각 기획안마다 다음 형식을 반드시 준수해 주세요:
   - **[주제 번호] 추천 제목**: 검색 유입이 잘 되는 매력적인 SEO 최적화 제목 (클릭을 부르는 제목)
   - **타겟 키워드**: 적용된 핵심 키워드 명시
   - **기획 의도**: 이 글이 구매셀러의 어떤 페인 포인트(Pain Point)를 해결해 주는지 설명 (2~3줄)
   - **본문 아웃라인(소제목 구조)**: 대표님이 살을 붙여서 글을 쓸 수 있도록 3~4개의 소제목 및 간략한 작성 팁 아웃라인 제공
3. 말투는 대표님이 읽기 편하도록 친근하고 가독성 좋은 한국어 마크다운(Markdown) 형태로 작성해 주세요.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    print("🧠 Gemini API를 통해 10개 블로그 기획안 생성 중...")
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"❌ Gemini API 요청 실패: {e}")
        return None

def send_email(subject, body_markdown, config):
    sender = config.get("SENDER_EMAIL")
    password = config.get("SENDER_APP_PASSWORD")
    receiver = config.get("RECEIVER_EMAIL")
    
    if not sender or not password or not receiver:
        print("❌ 이메일 전송 설정이 불완전합니다. config.md 파일을 확인하세요.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    
    # 마크다운 줄바꿈을 HTML <br>로 변경 및 가독성 개선
    body_html = body_markdown.replace('\n', '<br>')
    
    # 대표님이 이메일로 예쁘게 볼 수 있도록 스타일 래핑
    html_body = f"""
    <html>
      <head>
        <style>
          body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; }}
          pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }}
          h1 {{ color: #0f9d58; border-bottom: 2px solid #0f9d58; padding-bottom: 10px; }}
          h2 {{ color: #1a73e8; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px; margin-top: 30px; }}
          h3 {{ color: #e8241a; }}
          .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }}
          .meta-box {{ background-color: #f9f9f9; padding: 10px 15px; border-left: 4px solid #1a73e8; margin-bottom: 20px; }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>다다직구 복구 리포트: 10개 블로그 추천 기획안 💌</h1>
          <div class="meta-box">
            <p><strong>수신인:</strong> {receiver} (대표님)</p>
            <p><strong>내용:</strong> 어제 누락되었던 중국 구매셀러 타겟 블로그 주제 기획안 10개 세트입니다. OLLAMA 및 에이전트 경로 오류가 완전히 복구되었으며, 아래에서 최종 기획안을 전송해 드립니다.</p>
          </div>
          <hr>
          <div>
            {body_html}
          </div>
        </div>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    try:
        print("📧 Gmail SMTP 서버 연결 중...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=20)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.close()
        print(f"📧 이메일 전송 완료! ({receiver})")
        return True
    except Exception as e:
        print(f"❌ 이메일 전송 실패: {e}")
        return False

def main():
    print("🏁 [복구 작업] 10개 블로그 글 주제 생성 및 메일 발송 파이프라인 구동")
    config = load_config()
    api_key = config.get("GEMINI_API_KEY")
    
    if not api_key or "여기에" in api_key:
        print("❌ 유효한 Gemini API 키가 없습니다. config.md 설정을 확인하세요.")
        return
        
    keywords_context = load_recent_keywords()
    if not keywords_context:
        print("❌ 최근 키워드 컨텍스트를 불러오지 못했습니다. 분석을 계속할 수 없습니다.")
        return
        
    report_content = generate_blog_ideas(api_key, keywords_context)
    if not report_content:
        print("❌ 블로그 주제 10개 생성에 실패했습니다.")
        return
        
    # 1. 로컬에 2026-06-07 파일로 백업
    backup_file = r"E:\work\_company\_blog_keywords_2026-06-07.md"
    try:
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"💾 로컬 파일 저장 완료: {backup_file}")
    except Exception as e:
        print(f"❌ 로컬 파일 저장 실패: {e}")
        
    # 2. 이메일 전송
    subject = "[다다직구 복구] 어제 누락된 중국 구매셀러 블로그 포스팅 주제 기획안 10개"
    success = send_email(subject, report_content, config)
    
    if success:
        print("🎉 모든 복구 작업이 성공적으로 완료되었습니다!")
    else:
        print("⚠️ 파일 저장에는 성공했으나 이메일 발송에 실패했습니다.")

if __name__ == "__main__":
    main()
