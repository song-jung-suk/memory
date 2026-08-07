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
import html as html_lib

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
# 3. 워드프레스 기존 포스팅 제목 목록 수집 (중복 방지용)
# -------------------------------------------------------------
def get_existing_post_titles(blog_url):
    print("   [1/4] 기존 포스팅 제목 목록 수집 중...")
    api_url = f"{blog_url.rstrip('/')}/wp-json/wp/v2/posts?per_page=20"
    req = urllib.request.Request(
        api_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            titles = [html_lib.unescape(post.get("title", {}).get("rendered", "")) for post in data]
            return titles
    except Exception as e:
        print(f"❌ 기존 포스팅 제목 수집 실패: {e}")
        return []

# -------------------------------------------------------------
# 4. 워드프레스 최신글 추출 모듈 (WP JSON API 사용)
# -------------------------------------------------------------
def get_latest_wordpress_post(blog_url):
    print("   [2/4] 최신 워드프레스 포스팅 수집 중...")
    # wp-json API 엔드포인트
    api_url = f"{blog_url.rstrip('/')}/wp-json/wp/v2/posts?per_page=1"
    
    req = urllib.request.Request(
        api_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
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
# 5. Gemini API를 활용한 콘텐츠 생성 모듈 (REST API 사용)
# -------------------------------------------------------------
def generate_contents(post_title, post_link, post_content, existing_titles, api_key):
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
   - **중요 지침:** 이미지 단 한 장으로 스크롤을 멈추게 하는 **강력한 후킹 비주얼**을 기획하세요. 복잡한 배경 대신 강렬한 상징물이나 대비 효과를 사용하세요.
   - **텍스트 삽입 기획:** 구글 Flux 모델이 이미지 내에 **핵심 주제를 직관적으로 요약하는 굵고 트렌디한 영문 텍스트**를 정교하게 렌더링하도록 프롬프트를 구성해 주세요. (예: "SOURCING TRAP", "1688 vs CHINAGOODS" 등 블로그 글의 가장 핵심적인 후킹 키워드를 지정하여 프롬프트에 `with bold typography text "KEYWORD" written on it` 형태로 명시)
   - 구글 Flux 이미지 생성 AI가 디테일하게 그릴 수 있도록 영문(English) 프롬프트 1개를 작성해 주세요. (가로세로 비율은 1:1 인스타 피드용 지시어 포함)
   - 프롬프트에 어울리는 한국어 비주얼 컨셉 및 삽입된 텍스트의 디자인 의도 설명도 덧붙여 주세요.
   - 인스타그램 캡션 작성 시, 블로그 유입을 유도하기 위해 본문에 링크 클릭이 안 되므로 "프로필 링크의 블로그 바로가기를 통해 꿀팁을 확인하세요!" 와 같은 유도 문구와 어울리는 톤의 해시태그(#다다직구, #블로그제목 등)를 구성해 주세요.

2. 유튜브 쇼츠(Shorts)용 대본 및 영상 작업 기획서:
   - 쇼츠 영상은 약 40~50초 분량(내레이션 기준 약 120-150단어)의 빠르고 호기심을 자극하는 흐름으로 기획해 주세요.
   - **중요 지침:** 시청자 이탈을 막기 위해 **한 장면(Scene)당 길이를 5초 내외**로 짧고 컴팩트하게 구성해 주세요. (40~50초 영상 기준 총 8~10개 내외의 씬이 필요합니다.)
   - 먼저 디자이너 에이전트가 설계한 구글 Flux용 이미지 프롬프트를 씬(Scene)별로 매핑하여, 생성한 이미지들을 기반으로 숏폼 비디오 편집이 가능하도록 기획서를 구체적으로 짜주세요.
   - 형식:
     - 씬 번호 및 매핑 시간 (Scene 1 [00:00 - 00:05], Scene 2 [00:05 - 00:10]...)
     - 이미지 프롬프트 (영문): 해당 씬에 렌더링해서 깔아둘 구글 Flux용 영문 이미지 생성 프롬프트
     - 내레이션 (한국어): 대표님이 더빙하거나 AI 목소리로 읽을 대본 (씬당 5초 분량에 알맞게 컴팩트하게 작성)
     - 연출 및 자막 가이드: 화면 전환 효과나 텍스트 자막 위치 안내
   - 대본 마지막 부분에는 반드시 "자세한 정보와 제품 링크는 영상 설명란(또는 고정 댓글)의 다다직구 블로그 링크({post_link})를 클릭해서 확인해 보세요!" 라는 블로그 수익화 연계 멘트를 자연스럽게 넣어주세요.
   - **[추가 필수 항목]** 기획서 맨 아래에 다음 유튜브 등록용 메타데이터 세트를 생성해 주세요:
     1. **영상 설명문(Video Description):** 시청자의 호기심을 자극하고 본문 블로그 링크({post_link}) 클릭을 강하게 유도하는 간결한 3줄 요약 설명문.
     2. **태그 및 키워드(Tags & Keywords):** 유튜브 검색 상위 노출에 유리한 핵심 태그 10~15개 구성.
     3. **고정 댓글(Pinned Comment) 내용:** 유튜브 영상 업로드 시 댓글 상단에 고정해 둘 문구와 블로그 바로가기 링크({post_link}) 포함.

3. 💡 비서실장 추천: 차기 블로그 포스팅 추천 소재 (3개 세트)
   - **목적**: 대표님이 다음에 작성할 블로그 글의 영감을 얻기 위해, 타겟 고객이 열광하는 소재를 발굴합니다.
   - **중요 지침 (중복 절대 방지)**: 아래 나열된 [기존 포스팅 제목 목록]과 절대로 유사하거나 중복되지 않는 새로운 주제를 만드세요.
   - **키워드 반영**: 아래의 [중국 사입 핵심 키워드 라이브러리] 중 1~2개를 적절히 골라 자연스럽게 조합하여 만드세요.
   - **작성 포맷 (각 소재별)**:
     - **추천 주제(제목)**: 호기심을 자극하고 검색 친화적인 SEO 최적화 제목
     - **기획 의도 및 본문 요약 개요**: 글에 포함해야 할 핵심적인 내용과 소제목 구조를 3~5줄 내외의 깔끔한 개요(아웃라인)로 정리 (본문을 다 작성할 필요는 없으며, 대표님이 이 개요만 보고도 살을 붙여 직접 글을 쓸 수 있도록 아웃라인을 잘 잡아주세요.)

[기존 포스팅 제목 목록]
{chr(10).join('- ' + t for t in existing_titles) if existing_titles else '- 기존 포스팅 없음'}

[중국 사입 핵심 키워드 라이브러리]
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
    
    print("   [3/4] Gemini API를 통한 콘텐츠 생성 중 (약 5~10초 소요)...")
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        # 타임아웃을 120초로 대폭 늘려 안정적으로 마케팅 콘텐츠 생성을 대기합니다.
        with urllib.request.urlopen(req, timeout=120) as response:
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
            pass
            
        print("🧠 [Fallback] 로컬 LLM 서버(LM Studio)로 콘텐츠 생성 시도 중...")
        try:
            local_url = "http://127.0.0.1:1234/v1/chat/completions"
            
            # 활성화된 모델 이름 자동 감지
            local_model = "qwen3.5-4b"
            try:
                model_detect_req = urllib.request.Request("http://127.0.0.1:1234/v1/models")
                with urllib.request.urlopen(model_detect_req, timeout=5) as m_resp:
                    m_data = json.loads(m_resp.read().decode('utf-8'))
                    models = [m["id"] for m in m_data.get("data", [])]
                    if models:
                        local_model = models[0]
            except Exception:
                pass
                
            print(f"   로컬 모델 선택: {local_model}")
            
            local_prompt = prompt + "\n\n[중요] 로컬 LLM의 연산 부하를 줄이기 위해 모든 섹션의 분량을 대폭 축소하여 불필요한 설명은 완전히 생략하고 아주 짧고 명료하게 핵심만 작성해 주세요. (인스타 프롬프트 1개, 인스타 캡션 3줄 이내, 유튜브 쇼츠 대본은 Scene 3개 이내, 차기 추천 소재는 1개만 아주 간결하게 답변)"
            local_payload = {
                "model": local_model,
                "messages": [{"role": "user", "content": local_prompt}],
                "stream": False,
                "max_tokens": 2048
            }
            
            local_req = urllib.request.Request(
                local_url,
                data=json.dumps(local_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(local_req, timeout=240) as local_resp:
                local_result = json.loads(local_resp.read().decode('utf-8'))
                print(f"DEBUG local_result: {json.dumps(local_result, ensure_ascii=False)[:500]}")
                text = local_result['choices'][0]['message']['content'].strip()
                print(f"✅ [Fallback] 로컬 LLM으로 콘텐츠 생성 성공! (길이: {len(text)})")
                return text
        except Exception as local_err:
            print(f"❌ [Fallback] 로컬 LLM 생성 실패: {local_err}")
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
        # Gmail SMTP 표준 설정 및 타임아웃 15초 적용
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
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
    
    existing_titles = get_existing_post_titles(blog_url)
    print(f"📚 기존 포스팅 {len(existing_titles)}개 수집 완료 (중복 방지 필터 적용)")
    
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
        existing_titles,
        api_key
    )
    
    if not content_report:
        print("❌ 콘텐츠 생성에 실패했습니다.")
        return
        
    print("✨ 콘텐츠 생성 완료! 메일 전송 준비 중...")
    
    subject = f"[다다직구 자동화] '{post['title']}' 기반 인스타 & 쇼츠 마케팅 기획서"
    success = send_email(subject, content_report, config)
    
    if success or content_report:
        # 결과를 로컬 sessions 폴더에도 자동 저장/보관합니다.
        try:
            sys.path.append(r"E:\work\agents")
            from session_logger import save_session_artifact
            save_session_artifact("wordpress", "marketing_report.md", content_report)
        except Exception as se:
            print(f"⚠️ 세션 저장 중 오류 발생: {se}")
        
if __name__ == "__main__":
    main()
