import os
import re
import json
import urllib.request
import urllib.parse
import subprocess
import time
import sys
import io
import threading

# Windows 콘솔 인코딩 에러 방지
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -------------------------------------------------------------
# 1. 설정 및 경로 정의
# -------------------------------------------------------------
SECRETARY_CONFIG_PATH = r"E:\work\_company\_agents\secretary\config.md"
DEVELOPER_CONFIG_PATH = r"E:\work\_company\_agents\developer\config.md"
OFFSET_FILE_PATH = r"E:\work\.telegram_offset.json"
PIPELINE_SCRIPT_PATH = r"E:\work\agents\developer\wordpress_pipeline.py"
PYTHON_EXECUTABLE = r"C:\Users\qdson\AppData\Local\Programs\Python\Python310\python.exe"

# 글로벌 실행 상태 락 (Lock)
is_pipeline_running = False
pipeline_lock = threading.Lock()

# -------------------------------------------------------------
# 2. 마크다운 설정 파일 파싱 유틸리티
# -------------------------------------------------------------
def load_markdown_config(config_path):
    config = {}
    if not os.path.exists(config_path):
        return config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = r"-\s*([A-Z_]+)\s*:\s*[\"']?(.*?)[\"']?\s*$"
        matches = re.findall(pattern, content, re.MULTILINE)
        for key, val in matches:
            config[key] = val.strip().strip('"').strip("'")
    except Exception as e:
        print(f"⚠️ 설정 파일 로드 에러 ({config_path}): {e}")
    return config

# -------------------------------------------------------------
# 3. 텔레그램 API 유틸리티 (urllib 기반)
# -------------------------------------------------------------
def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ 텔레그램 메시지 전송 실패: {e}")
        return None

def get_telegram_updates(token, offset, timeout=30):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    payload = {
        "offset": offset,
        "timeout": timeout,
        "allowed_updates": ["message"]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout + 5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"🔍 업데이트 가져오기 대기 중... ({e})")
        return None

# -------------------------------------------------------------
# 4. 오프셋 저장 및 로드
# -------------------------------------------------------------
def load_offset():
    if os.path.exists(OFFSET_FILE_PATH):
        try:
            with open(OFFSET_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("offset", 0)
        except Exception:
            return 0
    return 0

def save_offset(offset):
    try:
        with open(OFFSET_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({"offset": offset}, f)
    except Exception as e:
        print(f"⚠️ 오프셋 저장 실패: {e}")

# -------------------------------------------------------------
# 5. 파이프라인 백그라운드 비동기 실행 본체
# -------------------------------------------------------------
def run_pipeline_worker(token, chat_id):
    global is_pipeline_running
    
    send_telegram_message(
        token, 
        chat_id, 
        "🚀 <b>다다직구 자동화 파이프라인 구동 시작!</b>\n콘텐츠 분석 및 메일 전송이 진행됩니다. 잠시만 기다려 주세요 (약 10~20초 소요)..."
    )
    
    cmd = [PYTHON_EXECUTABLE, "-u", PIPELINE_SCRIPT_PATH]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        stdout_accumulator = []
        stderr_accumulator = []
        
        progress_sent = {
            "WP_FETCH": False,
            "GEMINI_START": False,
            "MAIL_START": False
        }
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                stdout_accumulator.append(line)
                print(f"[Pipeline STDOUT] {line}")
                
                # 중간 단계 분석 및 텔레그램 진행 보고
                if "기존 포스팅" in line and not progress_sent["WP_FETCH"]:
                    send_telegram_message(token, chat_id, "📚 <b>[1단계 완료]</b> 기존 포스팅 수집 및 비교 분석 완료!")
                    progress_sent["WP_FETCH"] = True
                elif "Gemini 에이전트 팀 분석 시작" in line and not progress_sent["GEMINI_START"]:
                    send_telegram_message(token, chat_id, "🧠 <b>[2단계 완료]</b> 최신 블로그 글 수집 완료! Gemini AI 마케팅 에이전트 협업 분석을 시작합니다...")
                    progress_sent["GEMINI_START"] = True
                elif "메일 전송 준비" in line and not progress_sent["MAIL_START"]:
                    send_telegram_message(token, chat_id, "✨ <b>[3단계 완료]</b> 마케팅 기획 콘텐츠 생성 완료! 📧 이메일 전송을 시작합니다...")
                    progress_sent["MAIL_START"] = True
                    
        for err_line in process.stderr:
            stderr_accumulator.append(err_line.strip())
            print(f"[Pipeline STDERR] {err_line.strip()}", file=sys.stderr)
            
        return_code = process.poll()
        stdout_full = "\n".join(stdout_accumulator)
        stderr_full = "\n".join(stderr_accumulator)
        
        if return_code == 0 and "이메일 전송 완료" in stdout_full:
            post_match = re.search(r"📝 대상 포스팅: '(.*?)'", stdout_full)
            post_title = post_match.group(1) if post_match else "최신 포스팅"
            
            report = (
                f"✅ <b>마케팅 파이프라인 구동 성공!</b>\n\n"
                f"📝 <b>대상 글:</b> {post_title}\n"
                f"📧 <b>이메일 전송:</b> 완료! 수신함을 확인해 보세요.\n"
                f"💾 <b>로컬 백업:</b> 세션 디렉토리에 마크다운 리포트 저장 완료."
            )
            send_telegram_message(token, chat_id, report)
        else:
            error_msg = f"❌ <b>마케팅 파이프라인 구동 실패!</b> (Exit Code: {return_code})\n\n"
            if stderr_full:
                error_msg += f"⚠️ <b>상세 에러 로그:</b>\n<code>{stderr_full[:500]}</code>"
            elif "전송 실패" in stdout_full:
                error_match = re.search(r"❌ (이메일 전송 실패.*)", stdout_full)
                error_detail = error_match.group(1) if error_match else "이메일 인증 혹은 전송 오류 발생"
                error_msg += f"⚠️ <b>에러 원인:</b>\n<code>{error_detail}</code>"
            else:
                error_msg += "알 수 없는 에러가 발생하여 이메일이 발송되지 않았습니다."
                
            send_telegram_message(token, chat_id, error_msg)
            
    except Exception as e:
        send_telegram_message(token, chat_id, f"❌ <b>서브프로세스 실행 중 오류 발생:</b>\n<code>{str(e)}</code>")
    finally:
        with pipeline_lock:
            is_pipeline_running = False

# -------------------------------------------------------------
# 6. 메인 롱폴링 루프
# -------------------------------------------------------------
def main():
    global is_pipeline_running
    
    secretary_cfg = load_markdown_config(SECRETARY_CONFIG_PATH)
    token = secretary_cfg.get("TELEGRAM_BOT_TOKEN")
    chat_id = secretary_cfg.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 설정이 누락되었습니다.")
        sys.exit(1)
        
    print("====================================================")
    print("🤖 다다직구 텔레그램 비동기 리스너 서비스를 시작합니다...")
    print(f"📡 수신 대상 챗 ID: {chat_id}")
    print("====================================================")
    
    send_telegram_message(
        token, 
        chat_id, 
        "🤖 <b>다다직구 원격 조종 봇 활성화 (비동기 엔진)!</b>\n\n대기 상태에 진입했습니다. 이제 외부에서 <code>/run</code> 또는 <code>실행</code>이라고 입력하시면 비동기 스레드로 타임아웃 없이 파이프라인이 안전하게 가동됩니다. ✨"
    )
    
    offset = load_offset()
    
    while True:
        try:
            updates = get_telegram_updates(token, offset)
            if not updates or "result" not in updates:
                time.sleep(1)
                continue
                
            for update in updates["result"]:
                offset = update["update_id"] + 1
                save_offset(offset)
                
                message = update.get("message")
                if not message:
                    continue
                    
                msg_chat_id = str(message.get("chat", {}).get("id"))
                msg_text = (message.get("text") or "").strip()
                
                if msg_chat_id != chat_id:
                    print(f"⚠️ 허용되지 않은 사용자 접근 감지 (Chat ID: {msg_chat_id})")
                    send_telegram_message(
                        token, 
                        msg_chat_id, 
                        "🚫 <b>접근 권한이 없습니다.</b>\n이 봇은 다다직구 관리자만 조종할 수 있습니다."
                    )
                    continue
                
                if msg_text.startswith("/") or msg_text in ["실행", "시작", "run", "pipeline"]:
                    cmd_clean = msg_text.lower().replace("/", "")
                    
                    if cmd_clean in ["start", "help", "시작"]:
                        help_text = (
                            "🤖 <b>다다직구 마케팅 원격 비서 봇 도움말</b>\n\n"
                            "📢 <b>사용 가능한 명령어:</b>\n"
                            "👉 <code>/run</code> 또는 <code>실행</code> : 다다직구 자동화 파이프라인 즉시 구동 및 메일 전송\n"
                            "👉 <code>/추천 [상품명]</code> : 쿠팡/알리 3-트랙 원고 (쇼츠/인스타/블로그) 자동 생성\n"
                            "👉 <code>/status</code> : 현재 파이프라인 가동 상태 조회\n"
                            "👉 <code>/help</code> : 도움말 안내"
                        )
                        send_telegram_message(token, chat_id, help_text)
                        
                    elif cmd_clean in ["run", "pipeline", "실행"]:
                        with pipeline_lock:
                            if is_pipeline_running:
                                send_telegram_message(
                                    token, 
                                    chat_id, 
                                    "⚠️ <b>현재 파이프라인이 구동 중입니다.</b>\n이전 작업이 끝날 때까지 대기해 주세요!"
                                )
                                continue
                            else:
                                is_pipeline_running = True
                        
                        # 🧵 비동기 백그라운드 스레드로 파이프라인 구동 시작!
                        worker_thread = threading.Thread(
                            target=run_pipeline_worker, 
                            args=(token, chat_id)
                        )
                        worker_thread.daemon = True
                        worker_thread.start()
                        
                    elif cmd_clean.startswith("추천") or cmd_clean.startswith("affiliate") or cmd_clean.startswith("소싱"):
                        keyword = msg_text.replace("/추천", "").replace("/affiliate", "").replace("추천", "").strip()
                        if not keyword:
                            keyword = "알리익스프레스 가성비 소싱 추천 템"
                        send_telegram_message(token, chat_id, f"🛍️ <b>'{keyword}'</b> 기반으로 쇼츠, 인스타, 블로그 3-트랙 원고 생성을 시작합니다...")
                        
                        def run_affiliate_job(kw):
                            aff_cmd = [PYTHON_EXECUTABLE, "-u", r"E:\work\agents\developer\affiliate_pipeline.py", kw]
                            subprocess.run(aff_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                            
                        t = threading.Thread(target=run_affiliate_job, args=(keyword,))
                        t.daemon = True
                        t.start()
                    elif cmd_clean in ["status", "상태"]:
                        with pipeline_lock:
                            status_str = "🏃 <b>작업 중 (Running)</b>" if is_pipeline_running else "💤 <b>대기 중 (Idle)</b>"
                        send_telegram_message(token, chat_id, f"현재 파이프라인 상태: {status_str}")
                        
                    else:
                        send_telegram_message(token, chat_id, "❓ 알 수 없는 명령어입니다. <code>/help</code>를 입력해 보세요.")
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n👋 서비스를 안전하게 종료합니다.")
            send_telegram_message(token, chat_id, "🛑 <b>다다직구 원격 조종 리스너 서비스가 종료되었습니다.</b>")
            break
        except Exception as e:
            print(f"⚠️ 예외 발생: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
