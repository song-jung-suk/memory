# 📷 Instagram — @dadajikgu 계정 현재 올린 피드/릴스 게시글의 도달수, 참여율, 해시태그 효과 분석 보고 및 자동 배포 준비



📷 Instagram: 작업 시작합니다.

[CEO의 지시] 분석과 자동 배포 준비를 위해 먼저 dadajikgu 계정의 최근 게시물을 조회하고, 데이터 기반으로 도달·참여·해시태그 효과를 평가하는 것을 우선으로 진행합니다.

<read_file path="e:\work\_company\_agents\instagram\tools\feed_poster.json"/>
<run_command>cd "e:\work\_company\_agents\instagram\tools" && py -3 instagram_tool.py --latest-posts</run_command>

---
## 🛠️ 도구 실행 결과 (시스템 자동 실행)

### 🔧 실행: `cd "e:\work\_company\_agents\instagram\tools" && py -3 instagram_tool.py --latest-posts`
```
usage: instagram_tool.py [-h] [--test] [--insights] [--get-metrics] [--post]
                         [--image IMAGE] [--caption CAPTION]
instagram_tool.py: error: unrecognized arguments: --latest-posts
```
_❌ exit 2_

---
## 📁 파일 액션 결과

📖 읽기: e:\work\_company\_agents\instagram\tools\feed_poster.json (25줄, 0.9KB)
```
 1	{
 2	  "IMAGE_PATH": "",
 3	  "CAPTION": "인스타그램 업로드 테스트 📸 #테스트",
 4	  "PREVIEW": false,
 5	  "TELEGRAM_NOTIFY": true,
 6	  "_schema": {
 7	    "IMAGE_PATH": {
 8	      "label": "🖼️ 업로드할 이미지 경로",
 9	      "hint": "로컬 PC의 절대 경로를 입력해 주세요 (예: C:/Users/qdson/Documents/post.png)."
10	    },
...
```

[시스템: read_file 결과]
파일: e:\work\_company\_agents\instagram\tools\feed_poster.json (25줄)
```
 1	{
 2	  "IMAGE_PATH": "",
 3	  "CAPTION": "인스타그램 업로드 테스트 📸 #테스트",
 4	  "PREVIEW": false,
 5	  "TELEGRAM_NOTIFY": true,
 6	  "_schema": {
 7	    "IMAGE_PATH": {
 8	      "label": "🖼️ 업로드할 이미지 경로",
 9	      "hint": "로컬 PC의 절대 경로를 입력해 주세요 (예: C:/Users/qdson/Documents/post.png)."
10	    },
11	    "CAPTION": {
12	      "label": "📝 캡션 (본문 문구)",
13	      "hint": "인스타그램 게시글에 들어갈 내용과 해시태그를 입력해 주세요."
14	    },
15	    "PREVIEW": {
16	      "label": "👁️ 미리보기 모드",
17	      "hint": "실제 인스타그램에 업로드하지 않고 연동 흐름만 가상 시뮬레이션하려면 체크해 주세요."
18	    },
19	    "TELEGRAM_NOTIFY": {
20	      "label": "🔔 텔레그램으로 완료 알림 전송",
21	      "hint": "성공/실패 결과를 텔레그램 비서 채널로 자동 전송합니다."
22	    }
23	  }
24	}
25	
```
