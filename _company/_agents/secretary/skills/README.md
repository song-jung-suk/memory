# 📱 비서 영숙(Secretary) 전용 스킬 매니페스트

## 1. 텔레그램 수발신 및 보고 스킬 (`telegram_messenger`)
- **실행 스크립트**: `tools/telegram_setup.py`
- **역할**: 대표님과의 텔레그램 메신저 수발신, 주요 알림 발송 및 응답 처리
- **명령어**: `python _company/_agents/secretary/tools/telegram_setup.py`

## 2. 구글 캘린더 자동 연동 스킬 (`google_calendar_sync`)
- **실행 스크립트**: `tools/google_calendar_write.py` / `calendar_check.py`
- **역할**: 대표님 구글 캘린더 일정 조회, 각 에이전트의 마감일 동기화 및 신규 이벤트 자동 등록

## 3. 데일리 이메일 로컬 LLM 요약 보고 스킬 (`email_summarizer`) [★ 신규 구축]
- **실행 스크립트**: `tools/email_summarizer.py`
- **역할**: 중요 이메일 파싱 후 **로컬 LLM(Ollama)**을 활용해 개인정보 유출 없이 요약본을 작성하고 텔레그램으로 대표님께 데일리 브리핑 보고
- **명령어**: `python _company/_agents/secretary/tools/email_summarizer.py`
