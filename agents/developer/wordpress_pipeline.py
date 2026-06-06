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

# Windows 콘솔 이모지 인코딩 에러 방지
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -------------------------------------------------------------
# 1. 설정 로드 모듈
# -------------------------------------------------------------
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
        
    # 정규식을 사용해 마크다운 리스트 패턴 추출 (- KEY: VALUE)
    pattern = r"-\s*([A-Z_]+)\s*:\s*[\"']?(.*?)[\"']?\s*$"
    matches = re.findall(pattern, content, re.MULTILINE)
    
    for key, val in matches:
        if key in config:
            config[key] = val.strip().strip('"').strip("'")
            
    # 환경 변수 우선 확인 (Gemini API 키 등)
    env_gemini_key = os.environ.get("GEMINI_API_KEY")
    if env_gemini_key:
        config["GEMINI_API_KEY"] = env_gemini_key
        
    return config

# -------------------------------------------------------------
# 2. HTML 태그 제거 유틸리티
# -------------------------------------------------------------
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    # 다중 공백 및 줄바꿈 정리
    cleantext = re.sub(r'\n+', '\n', cleantext)
    return cleantext.strip()

# -------------------------------------------------------------
# 3. 워드프레스 최신글 추출 모듈 (WP JSON API 사용)
# -------------------------------------------------------------
def get_latest_wordpress_post(blog_url):
    # wp-json API 엔드포인트
    api_url = f"{blog_url.rstrip('/')}/wp-json/wp/v2/posts?per_page=1"
    
    req = urllib.request.Request(
        api_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data:
                print("❌ 최신 포스팅이 없습니다.")
                return None
                
            post = data[0]
            title = post.get("title", {}).get("rendered", "")
            link = post.get("link", "")
            content_html = post.get("content", {}).get("rendered", "")
            content_text = clean_html(content_html)
            
            # 본문이 너무 길면 LLM 토큰 절약을 위해 상위 3000자만 자름
            if len(content_text) > 3000:
                content_text = content_text[:3000] + "\n... (이하 생략)"
                
            return {
                "title": title,
                "link": link,
                "content": content_text
            }
    except Exception as e:
        print(f"❌ 워드프레스 수집 실패: {e}")
        return None

# -------------------------------------------------------------
# 4. Gemini API를 활용한 콘텐츠 생성 모듈 (REST API 사용)
# -------------------------------------------------------------
def generate_contents(post_title, post_link, post_content, api_key):
    if not api_key or "여기에" in api_key:
        raise ValueError("❌ 유효한 GEMINI_API_KEY가 없습니다. config.md 또는 환경변수를 확인해 주세요.")

    # 안정적인 v1beta 엔드포인트 및 Flash 모델 사용
    # 최신 성능이 좋은 gemini-1.5-flash 모델 적용
    endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
당신은 1인 기업 다다직구의 핵심 마케팅 에이전트 팀(디자이너, 카피라이터, 인스타그램 마케터, 유튜브 기획자)의 연합체입니다.
다음 제공되는 다다직구 워드프레스 블로그 글을 읽고, 이 포스팅의 홍보 및 블로그 유입(수익화)을 극대화하기 위한 두 가지 콘텐츠 세트를 작성해 주세요.

블로그 글 제목: {post_title}
블로그 글 링크: {post_link}
본문 요약:
\"\"\"
{post_content}
\"\"\"

---

[작성 지침]

1. 인스타그램용 이미지 생성 프롬프트 (구글 Flux용):
   - 본문의 내용과 분위기를 가장 잘 요약하여 설명할 수 있는 트렌디한 인스타 감성의 비주얼을 기획하세요.
   - 구글 Flux 이미지 생성 AI가 디테일하게 그릴 수 있도록 영문(English) 프롬프트 1개를 작성해 주세요. (가로세로 비율은 1:1 인스타 피드용 지시어 포함)
   - 프롬프트에 어울리는 한국어 비주얼 컨셉 설명도 덧붙여 주세요.
   - 인스타그램 캡션 작성 시, 블로그 유입을 유도하기 위해 본문에 링크 클릭이 안 되므로 "프로필 링크의 블로그 바로가기를 통해 꿀팁을 확인하세요!" 와 같은 유도 문구와 어울리는 톤의 해시태그(#다다직구, #블로그제목 등)를 구성해 주세요.

2. 유튜브 쇼츠(Shorts)용 대본 및 영상 작업 기획서:
   - 쇼츠 영상은 약 40~50초 분량(내레이션 기준 약 120-150단어)의 빠르고 호기심을 자극하는 흐름으로 기획해 주세요.
   - 먼저 디자이너 에이전트가 설계한 구글 Flux용 이미지 프롬프트를 씬(Scene)별로 3~4개 매핑하여, 생성한 이미지들을 기반으로 숏폼 비디오 편집이 가능하도록 기획서를 구체적으로 짜주세요.
   - 형식:
     - 씬 번호 (Scene 1, Scene 2...)
     - 이미지 프롬프트 (영문): 해당 씬에 렌더링해서 깔아둘 구글 Flux용 영문 이미지 생성 프롬프트
     - 내레이션 (한국어): 대표님이 더빙하거나 AI 목소리로 읽을 대본
     - 연출 및 자막 가이드: 화면 전환 효과나 텍스트 자막 위치 안내
   - 대본 마지막 부분에는 반드시 "자세한 정보와 제품 링크는 영상 설명란(또는 고정 댓글)의 다다직구 블로그 링크({post_link})를 클릭해서 확인해 보세요!" 라는 블로그 수익화 연계 멘트를 자연스럽게 넣어주세요.

---

출력 형식은 대표님이 메일로 읽기 편하도록 깔끔한 마크다운(Markdown) 포맷으로만 응답해 주세요.
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
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text
    except Exception as e:
        print(f"❌ Gemini API 요청 실패: {e}")
        try:
            if hasattr(e, 'read'):
                error_details = e.read().decode('utf-8')
                print(f"🔍 구글 API 에러 상세 내용: {error_details}")
        except Exception as read_err:
            print(f"에러 바디 읽기 실패: {read_err}")
        return None

# -------------------------------------------------------------
# 5. 이메일 전송 모듈 (SMTP TLS 사용)
# -------------------------------------------------------------
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
    
    # 이메일 클라이언트에서 보기 좋도록 마크다운을 간단한 HTML 형식으로 래핑하여 전송하거나 plain text로 전송
    # 메일 본문은 마크다운 텍스트를 그대로 전송하되, 줄바꿈이 유지되도록 처리
    body_html = body_markdown.replace('\n', '<br>')
    html_body = f"""
    <html>
      <head>
        <style>
          body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; }}
          pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }}
          h1, h2, h3 {{ color: #1a73e8; }}
          .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        </style>
      </head>
      <body>
        <div class="container">
          <h2>다다직구 마케팅 에이전트 리포트 💌</h2>
          <p>안녕하세요 대표님! 오늘 작성된 최신 워드프레스 포스팅 기반 인스타/유튜브 콘텐츠 자동 기획서입니다.</p>
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
        # Gmail SMTP 표준 설정
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.close()
        print(f"📧 이메일 전송 완료! ({receiver})")
        return True
    except Exception as e:
        print(f"❌ 이메일 전송 실패: {e}")
        return False

# -------------------------------------------------------------
# 6. 메인 실행 흐름
# -------------------------------------------------------------
def main():
    print("🚀 다다직구 자동 콘텐츠 파이프라인 구동 시작...")
    config = load_config()
    
    blog_url = config.get("BLOG_URL", "https://dadajikgu.com")
    print(f"🔗 블로그 수집 대상: {blog_url}")
    
    post = get_latest_wordpress_post(blog_url)
    if not post:
        print("❌ 분석할 포스팅을 찾지 못해 종료합니다.")
        return
        
    print(f"📝 대상 포스팅: '{post['title']}' ({post['link']})")
    
    api_key = config.get("GEMINI_API_KEY")
    # API 키가 비어있거나 기본 플레이스홀더 문구인 경우 예외처리 혹은 안내
    if not api_key or "여기에" in api_key:
        print("⚠️ GEMINI_API_KEY가 비어있습니다. Connect AI 시스템 환경 변수를 점검하거나 config.md에 기입해 주세요.")
        return
        
    print("🧠 Gemini 에이전트 팀 분석 시작...")
    content_report = generate_contents(
        post["title"], 
        post["link"], 
        post["content"], 
        api_key
    )
    
    if not content_report:
        print("❌ 콘텐츠 생성에 실패했습니다.")
        return
        
    print("✨ 콘텐츠 생성 완료! 메일 전송 준비 중...")
    
    subject = f"[다다직구 자동화] '{post['title']}' 기반 인스타 & 쇼츠 마케팅 기획서"
    success = send_email(subject, content_report, config)
    
    if success:
        # 결과를 로컬 sessions 폴더에도 기록해둡니다.
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        session_dir = f"E:\\work\\sessions\\{timestamp}"
        os.makedirs(session_dir, exist_ok=True)
        report_file = os.path.join(session_dir, "marketing_report.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(content_report)
        print(f"💾 로컬 세션 파일로도 저장 완료: {report_file}")
        
if __name__ == "__main__":
    main()
