@echo off
chcp 65001 > NUL
echo =======================================================
echo Starting Dadajikgu Telegram Remote Listener...
echo =======================================================
echo.

"C:\Users\qdson\AppData\Local\Programs\Python\Python310\python.exe" -u "E:\work\agents\developer\telegram_listener.py"

echo.
echo =======================================================
echo Telegram Listener stopped.
echo =======================================================
pause
