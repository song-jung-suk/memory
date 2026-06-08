#!/usr/bin/env python3
import os
import json
import urllib.parse
import urllib.request
import sys

# Windows 콘솔 utf-8 설정
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "google_calendar_write.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("❌ 설정 파일이 존재하지 않습니다. 경로를 확인해 주세요:", CONFIG_PATH)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print("💾 캘린더 설정 파일(google_calendar_write.json) 갱신 완료!")

def main():
    print("=== Google Calendar OAuth2 수동 인증 및 토큰 갱신 ===")
    cfg = load_config()
    
    client_id = cfg.get("CLIENT_ID", "").strip()
    client_secret = cfg.get("CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        print("❌ CLIENT_ID 또는 CLIENT_SECRET가 누락되었습니다.")
        sys.exit(1)
        
    # 구글 OAuth 클라이언트 유형에 따라 redirect_uri를 시도합니다.
    # 일반적으로 데스크톱 앱은 http://localhost 또는 http://127.0.0.1 을 사용합니다.
    # 오류가 나면 포트 번호(예: :8080)를 추가해 보세요.
    redirect_uri = "http://localhost"
    
    print("\n[단계 1] 아래의 웹 주소를 복사하여 브라우저 주소창에 붙여넣고 로그인해 주세요:")
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.events",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    print("\n" + auth_url + "\n")
    
    print("[단계 2] 로그인을 완료하면 브라우저 주소창이 다음처럼 변경되며 빈 페이지 또는 에러가 뜹니다.")
    print("  예시: http://localhost/?code=4/0Adyx...&scope=...")
    print("  이 변경된 주소창의 전체 URL을 복사하여 아래에 입력하고 Enter를 눌러주세요.")
    print("  (만약 redirect_uri_mismatch 에러가 뜬다면, 구글 클라우드 콘솔에 등록된 리디렉션 URI와 일치하지 않는 것입니다.)")
    
    try:
        url_input = input("\n복사한 URL 입력: ").strip()
    except KeyboardInterrupt:
        print("\n취소되었습니다.")
        sys.exit(0)
        
    if not url_input:
        print("❌ URL이 입력되지 않았습니다.")
        sys.exit(1)
        
    # URL에서 code 파라미터 추출
    code = ""
    if "code=" in url_input:
        parsed_url = urllib.parse.urlparse(url_input)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        code = query_params.get("code", [""])[0]
    else:
        code = url_input # 통째로 입력한 경우 대비
        
    if not code:
        print("❌ 입력한 URL에서 인증 코드(code)를 추출하지 못했습니다.")
        sys.exit(1)
        
    print("\n[단계 3] 구글 서버와 통신하여 Refresh Token을 획득하는 중...")
    
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        token_url, 
        data=data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            refresh_token = res_data.get("refresh_token")
            
            if not refresh_token:
                # refresh_token이 안 오는 경우는 이미 권한이 부여되어 있고 prompt=consent가 누락되었을 때입니다.
                print("⚠️ Refresh Token을 받지 못했습니다. (Access Token만 발급됨)")
                print("   만약 기존 계정에 승인이 남아있다면, 구글 계정 보안 설정에서 권한을 삭제한 후 다시 시도해 주세요.")
                sys.exit(1)
                
            cfg["REFRESH_TOKEN"] = refresh_token
            # 연결 시각 및 상태 갱신
            import datetime
            cfg["_CONNECTED_AT"] = datetime.datetime.utcnow().isoformat() + "Z"
            
            save_config(cfg)
            print("\n✅ 구글 캘린더 자격증명(Refresh Token) 수동 갱신 성공!")
            
    except Exception as e:
        print(f"\n❌ 토큰 교환 실패: {e}")
        try:
            if hasattr(e, 'read'):
                print("상세 에러 내용:", e.read().decode('utf-8'))
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
