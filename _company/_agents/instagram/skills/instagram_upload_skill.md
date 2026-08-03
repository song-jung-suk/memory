# 📷 Instagram 에이전트 — 인스타그램 자동 업로드 스킬 및 행동 수칙

이 지침은 **Meta Graph API v23.0 최신 표준** 및 보안 수칙을 준수하여 인스타그램 콘텐츠를 업로드하는 스킬 매니페스트입니다.

---

## 🛠️ 업로드 실행 로직 (`InstaUploader` Class)

```python
import requests
import time

class InstaUploader:
    """Instagram Graph API v23.0 Upload Engine"""
    def __init__(self, account_id, access_token):
        self.acc_id = account_id
        self.token = access_token
        self.version = "v23.0" # 최신 v23.0 규격 적용
        self.base_url = f"https://graph.instagram.com/{self.version}/{self.acc_id}"

    def upload_image(self, image_url, caption=""):
        # 1. 미디어 컨테이너 생성 (Image / Reel)
        r = requests.post(f"{self.base_url}/media", data={
            "image_url": image_url,
            "caption": caption,
            "access_token": self.token
        }, timeout=30)
        res = r.json()
        
        if "error" in res:
            error_info = res["error"]
            raise RuntimeError(f"[Code {error_info.get('code')}] {error_info.get('message')}")
            
        creation_id = res.get("id")
        
        # 2. 서버 미디어 처리 대기 (Processing Wait)
        print(f"⏳ 서버 처리 중... (Creation ID: {creation_id})")
        time.sleep(30) 

        # 3. 최종 발행 (Publish container)
        publish_r = requests.post(f"{self.base_url}/media_publish", data={
            "creation_id": creation_id,
            "access_token": self.token
        }, timeout=30)
        publish_res = publish_r.json()
        
        if "error" in publish_res:
            error_info = publish_res["error"]
            raise RuntimeError(f"[Publish Code {error_info.get('code')}] {error_info.get('message')}")
            
        return publish_res.get("id")
```

---

## 🛡️ 핵심 행동 수칙 (Constraints)

1. **정확한 경로 검증**: 미디어 URL은 반드시 인터넷 외부에서 접속 가능한 **공개 URL (`http://` 또는 `https://`)**이어야 하며, 로컬 파일인 경우 임시 공개 서버(Catbox 등)에 업로드 후 전달한다.
2. **토큰 보안 마스킹**: 콘솔 출력, 세션 보고서, 로그 파일 등 대화 및 출력 화면에 노출되는 Access Token은 앞 8자리/뒤 8자리를 제외하고 마스킹(`IGAAkzpd…gyawZDZD`)하여 보안을 유지한다.
3. **상태 모니터링 및 예외 처리**:
   - HTTP/API 에러 발생 시 `OAuthException` 또는 에러 코드를 분석하여 유저에게 명확한 해결 가이드(토큰 갱신, URL 만료 안내 등)를 제공한다.
   - 업로드 성공 시 포스트 ID와 함께 텔레그램으로 완료 보고를 발송한다.
