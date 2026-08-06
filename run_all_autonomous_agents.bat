@echo off
chcp 65001 > NUL
echo =======================================================
echo 🤖 Connect AI 24시간 자율 에이전트 통합 가동 시스템
echo =======================================================
echo.
echo 1. [영숙 비서] 캘린더 & 이메일 출근 모닝 브리핑 텔레그램 전송 중...
"C:\Users\qdson\AppData\Local\Programs\Python\Python310\python.exe" "C:\Users\qdson\.gemini\antigravity-ide\brain\2b8eb95e-bd29-4512-aa3b-02e46b1c30e1\scratch\morning_briefing.py"

echo 2. 텔레그램 원격 리스너 (명령어 대기) 가동 중...
start "Connect AI - Telegram Listener" /min "C:\Users\qdson\AppData\Local\Programs\Python\Python310\python.exe" -u "E:\work\agents\developer\telegram_listener.py"

echo 3. 24시간 오토 플래너 (6시간 주기 트렌드 분석 및 어필리에이트 생성) 가동 중...
start "Connect AI - Auto Planner" /min "C:\Users\qdson\AppData\Local\Programs\Python\Python310\python.exe" -u "E:\work\_company\_agents\youtube\tools\auto_planner.py"

echo.
echo =======================================================
echo ✅ 모든 자율 에이전트 서비스가 백그라운드에서 가동되었습니다.
echo 컴퓨터를 켜두시면 24시간 자율 모드로 작동합니다.
echo =======================================================
pause
