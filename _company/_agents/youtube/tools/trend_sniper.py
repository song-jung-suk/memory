#!/usr/bin/env python3
"""Trend Sniper — pulls top YouTube videos for target keywords, asks a local
LLM (Ollama/LM Studio) to extract the algorithmic patterns, and writes a
planning report next to this script.

Shared keys (API key, OLLAMA_URL, MODEL) come from youtube_account.json so
you only set them once. Per-tool keys (TARGET_KEYWORDS) come from
trend_sniper.json. If a key exists in both, trend_sniper.json wins.

Requires:  pip install google-api-python-client requests
"""
import os, json, time, random, datetime, sys, io

# 윈도우 환경 인코딩 오류 방지는 PYTHONIOENCODING 환경변수로 제어하거나 아래 buffer 래핑을 씁니다.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "trend_sniper.json")
ACCOUNT_PATH = os.path.join(HERE, "youtube_account.json")
REPORT_PATH = os.path.join(HERE, "trend_sniper_report.md")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 설정 파일을 읽을 수 없어요: {CONFIG_PATH}\n{e}")
        sys.exit(1)

def load_account():
    try:
        if os.path.exists(ACCOUNT_PATH):
            with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _shared(cfg, acct, key, default=""):
    """Per-tool config wins; falls back to shared account; finally default."""
    v = cfg.get(key)
    if v not in (None, "", []):
        return v
    v = acct.get(key)
    if v not in (None, "", []):
        return v
    return default

def main():
    cfg = load_config()
    acct = load_account()
    api_key = (_shared(cfg, acct, "YOUTUBE_API_KEY") or "").strip()
    if not api_key:
        print("⚠️  YOUTUBE_API_KEY가 비어있어요. youtube_account.json 또는 trend_sniper.json에 입력하세요.")
        print("   발급: https://console.cloud.google.com/ → YouTube Data API v3 사용 설정 → 사용자 인증 정보 → API 키")
        sys.exit(1)
    target_keywords = cfg.get("TARGET_KEYWORDS", [])
    if not target_keywords:
        print("⚠️  TARGET_KEYWORDS가 비어있어요. 분석할 키워드를 1개 이상 추가하세요.")
        sys.exit(1)
    ollama_url = (_shared(cfg, acct, "OLLAMA_URL", "http://127.0.0.1:11434") or "http://127.0.0.1:11434").rstrip("/")
    model = _shared(cfg, acct, "MODEL", "") or ""
    pick = min(2, len(target_keywords))
    chosen = random.sample(target_keywords, pick)

    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ google-api-python-client가 설치되지 않았어요.")
        print("   설치: pip install google-api-python-client requests")
        sys.exit(1)
    try:
        import requests
    except ImportError:
        print("❌ requests가 설치되지 않았어요. pip install requests")
        sys.exit(1)

    print(f"\n🎯 [트렌드 스나이퍼] 키워드 {chosen} 스캔 시작...")
    youtube = build('youtube', 'v3', developerKey=api_key)
    last_month = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    sniper_data = []
    for q in chosen:
        print(f"📡 [{q}] 검색 중...")
        try:
            req = youtube.search().list(
                part="snippet", q=f"{q} #shorts", maxResults=5, order="viewCount",
                publishedAfter=last_month, type="video", videoDuration="short"
            )
            res = req.execute()
            for item in res.get('items', []):
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                sniper_data.append(f"[{q}] 채널: {channel} | 제목: {title}")
        except Exception as e:
            print(f"❌ 검색 오류 ({q}): {e}")

    if not sniper_data:
        print("❌ 수집된 데이터 없음. API 키 한도/네트워크 확인.")
        sys.exit(1)

    data_text = "\n".join(sniper_data)
    prompt = f"""당신은 유튜브 알고리즘 마스터마인드입니다. 아래는 최근 30일 떡상 영상입니다.

[키워드] {', '.join(chosen)}
[데이터]
{data_text}

분석해서 마크다운 보고서를 작성하세요. 각 항목별로 장황한 설명은 배제하고 핵심 위주로 아주 짧고 명료하게(전체 500자 이내) 작성하세요. 반드시 3섹션:
1. 🌍 트렌드 해킹 분석 — 어떤 패턴이 조회수를 끌고 있는지 (핵심 포인트 2개)
2. 🎯 빈집 털기 전략 — 차별화 가능한 틈새 주제 (핵심 포인트 2개)
3. 🎬 파괴적 영상 기획안 — 썸네일 카피 1개, 제목 2개, 후킹 오프닝(첫 5초)
"""

    # v2.89.70 — LM Studio (OpenAI 호환 API) + Ollama 둘 다 지원. URL/포트로 자동 감지.
    is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
    print(f"🧠 [LLM 분석 중... 엔진: {'LM Studio' if is_lm_studio else 'Ollama'}]")

    # 모델 자동 선택 — 엔진별로 다른 endpoint
    if not model:
        try:
            if is_lm_studio:
                base = ollama_url.rstrip('/')
                if not base.endswith('/v1'):
                    base = base + '/v1'
                r = requests.get(f"{base}/models", timeout=3)
                r.raise_for_status()
                models = [m["id"] for m in r.json().get("data", [])]
            else:
                r = requests.get(f"{ollama_url}/api/tags", timeout=3)
                r.raise_for_status()
                models = [m["name"] for m in r.json().get("models", [])]
            if models:
                model = models[0]
                print(f"   자동 선택 모델: {model}")
        except Exception:
            print("⚠️ 로컬 LLM 서버 미응답 -> 백업 처리 모드로 진입")

    # 1. 로컬 LLM 호출 시도
    report = ""
    if model:
        try:
            if is_lm_studio:
                base = ollama_url.rstrip('/')
                if not base.endswith('/v1'):
                    base = base + '/v1'
                r = requests.post(
                    f"{base}/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "max_tokens": 1024,
                    },
                    timeout=3,
                )
                r.raise_for_status()
                report = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                r = requests.post(
                    f"{ollama_url}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=3,
                )
                r.raise_for_status()
                report = r.json().get("response", "").strip()
        except Exception as e:
            print(f"⚠️ 로컬 LLM 호출 미연결/실패 ({e}) -> 백업 처리 진행")

    # 2. 로컬 LLM 미연결 시 Gemini API 백업 생성
    if not report:
        dev_cfg_path = os.path.abspath(os.path.join(HERE, "..", "..", "developer", "config.md"))
        gemini_key = acct.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not gemini_key and os.path.exists(dev_cfg_path):
            try:
                with open(dev_cfg_path, "r", encoding="utf-8") as f:
                    m = re.search(r"-\s*GEMINI_API_KEY\s*:\s*[\"']?(.*?)[\"']?\s*$", f.read(), re.M)
                    if m: gemini_key = m.group(1).strip().strip('"').strip("'")
            except Exception: pass
        if gemini_key:
            try:
                import urllib.request
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=20) as res:
                    res_data = json.loads(res.read().decode('utf-8'))
                    report = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                    print("🌐 [백업 Gemini API로 트렌드 분석 완료]")
            except Exception as ge:
                print(f"❌ 백업 Gemini API도 실패: {ge}")

    if not report:
        print("❌ 보고서 생성 실패")
        sys.exit(1)

    print("\n" + "="*60)
    print(report)
    print("="*60)

    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n\n# 🎯 트렌드 스나이핑 보고서 — {now}\n")
        f.write(f"## 📡 키워드: {', '.join(chosen)}\n\n")
        f.write(report)
        f.write("\n\n---\n")
    print(f"\n✅ 보고서 저장: {REPORT_PATH}")

if __name__ == "__main__":
    main()
