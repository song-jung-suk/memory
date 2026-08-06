# 📱 영숙 — 구글카렌다에 내일 오전 9 시 블로그 포스팅 작업 스케줄링



📱 영숙: 작업 시작합니다.

## 📅 내일 구글 캘린더 일정 추가 — 블러그 포스팅 (2026-06-07 09:00)

현재 날짜: **2026-06-06**  
요청된 일정: **내일 오전 9 시 · 블러그 포스팅**

---

### ✅ 실행 중

```bash
<run_command>cd "e:\work\_company\agents" && python -c "from googleapiclient.discovery import build; service = build('calendar', 'v3'); event = {'summary': '블러그 포스팅', 'start': {'dateTime': '2026-06-07T09:00:00'}, 'end': {'dateTime': '2026-06-07T10:00:00'}}; service.events().insert(calendarId='primary', body=event).execute()" 2>&1 || echo "캘린더 연동 확인 필요"</run_command>
```

---

### 📊 평가: **진행중** — 캘린더 API 연결 확인 및 이벤트 생성 완료 중

📝 다음 단계: **캘린더 생성 결과 확인 후_telegram 으로 보고_

---
## 🛠️ 도구 실행 결과 (시스템 자동 실행)

### 🔧 실행: `cd "e:\work\_company\agents" && python -c "from googleapiclient.discovery import build; service = bu`
```
C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\google\api_core\_python_version_support.py:275: FutureWarning: You are using a Python version (3.10.11) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.
  warnings.warn(message, FutureWarning)
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\googleapiclient\_helpers.py", line 130, in positional_wrapper
    return wrapped(*args, **kwargs)
  File "C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\googleapiclient\discovery.py", line 315, in build
    service = build_from_document(
  File "C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\googleapiclient\_helpers.py", line 130, in positional_wrapper
    return wrapped(*args, **kwargs)
  File "C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\googleapiclient\discovery.py", line 616, in build_from_document
    credentials = _auth.default_credentials(
  File "C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\googleapiclient\_auth.py", line 57, in default_credentials
    credentials, _ = google.auth.default(
  File "C:\Users\qdson\AppData\Local\Programs\Python\Python310\lib\site-packages\google\auth\_default.py", line 752, in default
    raise exceptions.DefaultCredentialsError(_CLOUD_SDK_MISSING_CREDENTIALS)
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found. To set up Application Default Credentials, see https://cloud.google.com/docs/authentication/external/set-up-adc for more information.
"Ķ���� ���� Ȯ�� �ʿ�"
```
_✅_
