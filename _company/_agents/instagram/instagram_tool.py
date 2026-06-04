#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📷 Instagram Agent Automation Tool
Meta Graph API를 사용하여 인스타그램 비즈니스 계정의 정보를 수집하고 포스팅을 자동으로 업로드하는 프로덕션 레벨 도구입니다.
"""
import os
import sys
import re
import json
import urllib.request
import urllib.parse

# CP949 인코딩 안전 조치
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))

# 동적 디렉토리 파싱: config.md가 실제 존재하는 폴더를 AGENT_ROOT로 결정
def _find_agent_root():
    cands = [
        HERE,                                       # e:\work\_company\_agents\instagram
        os.path.dirname(HERE),                      # HERE가 tools일 때 부모 경로
        os.path.abspath(os.path.join(HERE, "..")),  # 기타 상위
    ]
    for c in cands:
        if os.path.exists(os.path.join(c, "config.md")):
            return c
    return HERE

AGENT_ROOT = _find_agent_root()
CONFIG_PATH = os.path.join(AGENT_ROOT, "config.md")
ACTIVITY_LOG = os.path.join(AGENT_ROOT, "activity.log")

def _log(msg, kind="info"):
    prefix = {"info": "📋", "ok": "✅", "warn": "⚠️ ", "err": "❌", "step": "▸"}.get(kind, "•")
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)

def log_activity(action, status, details=""):
    """모든 외부 행동을 activity.log에 기록 (감사 목적)"""
    try:
        from datetime import datetime
        now = datetime.now().isoformat()
        with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{now}] ACTION: {action} | STATUS: {status} | DETAILS: {details}\n")
    except Exception:
        pass

def load_config():
    """config.md에서 Meta Graph API 연동 토큰 안전 로드"""
    creds = {"META_ACCESS_TOKEN": "", "INSTAGRAM_BUSINESS_ID": ""}
    if not os.path.exists(CONFIG_PATH):
        _log(f"설정 파일 없음: {CONFIG_PATH}", "err")
        return creds
    
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 정규표현식으로 토큰 추출
        token_match = re.search(r"-\s*META_ACCESS_TOKEN:\s*(.*)", content)
        id_match = re.search(r"-\s*INSTAGRAM_BUSINESS_ID:\s*(.*)", content)
        
        if token_match:
            creds["META_ACCESS_TOKEN"] = token_match.group(1).strip()
        if id_match:
            creds["INSTAGRAM_BUSINESS_ID"] = id_match.group(1).strip()
    except Exception as e:
        _log(f"설정 로드 실패: {e}", "err")
        
    return creds

def make_request(url, method="GET", data=None, headers=None):
    """표준 라이브러리 urllib를 이용해 안전하게 API 요청 수행"""
    if headers is None:
        headers = {}
    
    req_data = None
    if data:
        if isinstance(data, dict):
            req_data = urllib.parse.urlencode(data).encode("utf-8")
        else:
            req_data = data
            
    req = urllib.request.Request(url, data=req_data, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
        
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_body = e.reason
        return e.code, err_body
    except Exception as e:
        return 500, {"error": str(e)}

def test_connection():
    """인스타그램 계정 정보 정상 조회를 통해 연동 상태 테스트"""
    creds = load_config()
    token = creds["META_ACCESS_TOKEN"]
    biz_id = creds["INSTAGRAM_BUSINESS_ID"]
    
    if not token:
        _log("META_ACCESS_TOKEN이 비어 있습니다. config.md를 먼저 채워주세요.", "warn")
        return False
        
    _log("1단계: 액세스 토큰이 접근 가능한 모든 페이스북 페이지 및 연동된 인스타그램 비즈니스 계정 탐색 중...", "step")
    # /me/accounts 호출하여 연동 목록 자동 스캔
    scan_url = f"https://graph.facebook.com/v19.0/me/accounts?fields=name,id,instagram_business_account{{id,username,name}}&access_token={token}"
    s_code, s_res = make_request(scan_url)
    
    found_accounts = []
    if s_code == 200 and isinstance(s_res, dict) and "data" in s_res:
        for page in s_res["data"]:
            page_name = page.get("name")
            page_id = page.get("id")
            insta_acc = page.get("instagram_business_account")
            if insta_acc:
                found_accounts.append({
                    "page_name": page_name,
                    "page_id": page_id,
                    "insta_id": insta_acc.get("id"),
                    "insta_username": insta_acc.get("username"),
                    "insta_name": insta_acc.get("name")
                })
                
    if found_accounts:
        _log("💡 [지능형 탐색기] 연동 가능한 인스타그램 비즈니스 계정을 발굴했습니다!", "ok")
        print("\n=======================================================")
        print(" [발견된 연동 가능 인스타그램 계정 목록]")
        print("-------------------------------------------------------")
        for i, acc in enumerate(found_accounts):
            print(f" {i+1}번 후보:")
            print(f"   • 페이스북 페이지명: {acc['page_name']} (ID: {acc['page_id']})")
            print(f"   • 진짜 인스타 비즈니스 ID: {acc['insta_id']} (계정: @{acc['insta_username']})")
            print("-------------------------------------------------------")
        print("=======================================================\n")
        
        # 만약 현재 입력된 ID가 다르고 첫 번째 인스타 계정이 발견되면 자동 제안
        best_id = found_accounts[0]["insta_id"]
        if biz_id != best_id:
            _log(f"👉 config.md의 INSTAGRAM_BUSINESS_ID를 [{best_id}] 로 변경하여 저장해 주세요!", "ok")
            _log(f"   (도우미가 이번 테스트만 임시로 발굴해낸 진짜 ID [{best_id}]로 연동 검증을 계속 진행해 드릴게요!)\n", "info")
            biz_id = best_id
    else:
        _log("⚠️  [지능형 탐색기] 토큰이 관리하는 페이스북 페이지 중 연동된 인스타그램 비즈니스 계정을 찾지 못했습니다.", "warn")
        _log("   인스타그램 계정이 '비즈니스(프로페셔널) 계정'으로 전환되었는지, 페이스북 페이지와 제대로 연결되었는지 반드시 확인해 주세요.", "warn")

    if not biz_id:
        _log("INSTAGRAM_BUSINESS_ID가 비어 있어 더 이상 테스트를 진행할 수 없습니다.", "err")
        return False

    # Meta Graph API 호출
    _log(f"2단계: 최종 결정된 인스타그램 비즈니스 ID [{biz_id}]로 연동 검증 수행 중...", "step")
    url = f"https://graph.facebook.com/v19.0/{biz_id}?fields=username,name,biography,followers_count,media_count&access_token={token}"
    code, res = make_request(url)
    
    # [폴백 적용] biography 등의 세부 필드 미지원으로 400 에러 발생 시, 필수 기본정보(username, name)로 재조회
    if code != 200 and isinstance(res, dict) and "biography" in res.get("error", {}).get("message", ""):
        _log("일부 세부 필드(biography)가 활성화되지 않아 기본 필드(username, name)로 다시 연동을 검증합니다...", "warn")
        url = f"https://graph.facebook.com/v19.0/{biz_id}?fields=username,name&access_token={token}"
        code, res = make_request(url)
    
    if code == 200:
        _log(f"인스타그램 연동 확인 성공! 계정명: @{res.get('username')}", "ok")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        log_activity("TEST_CONNECTION", "SUCCESS", f"Account: @{res.get('username')}")
        return True
    else:
        _log(f"인스타그램 연동 실패 (코드 {code}): {res}", "err")
        if code == 400 and "deprecated" in str(res):
            _log("\n💡 가이드: 이 에러는 입력하신 ID가 진짜 인스타그램 비즈니스 ID가 아닌 '페이스북 개인 ID'이기 때문에 발생합니다.", "warn")
            _log("   위에 안내해 드린 [지능형 탐색기]의 진짜 인스타 ID 목록을 확인하여 config.md에 적어주세요.", "warn")
        log_activity("TEST_CONNECTION", "FAILED", f"Error: {res}")
        return False

def get_insights():
    """인스타그램 비즈니스 계정 핵심 참여도 분석 및 수집"""
    creds = load_config()
    token = creds["META_ACCESS_TOKEN"]
    biz_id = creds["INSTAGRAM_BUSINESS_ID"]
    
    if not token or not biz_id:
        _log("API 설정 누락 (META_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ID)", "err")
        return None
        
    # 도달(reach), 팔로워 증감(follower_count) 수집 (profile_views는 특수 파라미터가 필요해 제외)
    metrics = "reach,follower_count"
    url = f"https://graph.facebook.com/v19.0/{biz_id}/insights?metric={metrics}&period=day&access_token={token}"
    
    code, res = make_request(url)
    if code == 200:
        _log("인스타그램 계정 인사이트 데이터 수집 성공", "ok")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        log_activity("GET_INSIGHTS", "SUCCESS", f"Metrics gathered: {metrics}")
        return res
    else:
        _log(f"인사이트 수집 실패 (코드 {code}): {res}", "err")
        log_activity("GET_INSIGHTS", "FAILED", f"Error: {res}")
        return None

def get_media_list(limit=10):
    """최근 업로드된 인스타그램 미디어 목록 수집"""
    creds = load_config()
    token = creds["META_ACCESS_TOKEN"]
    biz_id = creds["INSTAGRAM_BUSINESS_ID"]
    
    if not token or not biz_id:
        _log("API 설정 누락 (META_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ID)", "err")
        return None
        
    fields = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count"
    url = f"https://graph.facebook.com/v19.0/{biz_id}/media?fields={fields}&limit={limit}&access_token={token}"
    
    code, res = make_request(url)
    if code == 200:
        _log("인스타그램 미디어 목록 수집 성공", "ok")
        return res.get("data", [])
    else:
        _log(f"미디어 목록 수집 실패 (코드 {code}): {res}", "err")
        return None

def get_comments(media_id, limit=5):
    """특정 미디어의 댓글 수집"""
    creds = load_config()
    token = creds["META_ACCESS_TOKEN"]
    
    if not token:
        _log("META_ACCESS_TOKEN 누락", "err")
        return []
        
    url = f"https://graph.facebook.com/v19.0/{media_id}/comments?fields=id,text,timestamp,username&limit={limit}&access_token={token}"
    
    code, res = make_request(url)
    if code == 200:
        return res.get("data", [])
    else:
        return []

def resolve_telegram():
    token, chat = "", ""
    brain_root = os.path.dirname(os.path.dirname(AGENT_ROOT))
    sec_config_md = os.path.join(brain_root, "secretary", "config.md")
    sec_json = os.path.join(brain_root, "secretary", "tools", "telegram_setup.json")
    
    if os.path.exists(sec_json):
        try:
            with open(sec_json, "r", encoding="utf-8") as f:
                s_cfg = json.load(f)
            token = (s_cfg.get("TELEGRAM_BOT_TOKEN") or "").strip()
            chat = (s_cfg.get("TELEGRAM_CHAT_ID") or "").strip()
        except Exception:
            pass

    if not token or not chat:
        if os.path.exists(sec_config_md):
            try:
                with open(sec_config_md, "r", encoding="utf-8") as f:
                    content = f.read()
                m_token = re.search(r"TELEGRAM_BOT_TOKEN\s*[:：=]\s*([A-Za-z0-9:_\-]+)", content)
                m_chat = re.search(r"TELEGRAM_CHAT_ID\s*[:：=]\s*(-?\d+)", content)
                if m_token: token = m_token.group(1).strip()
                if m_chat: chat = m_chat.group(1).strip()
            except Exception:
                pass
                
    return token, chat

def send_telegram_notification(token, chat, text):
    if not token or not chat:
        _log("텔레그램 알림 설정이 누락되어 알림을 건너뜁니다.", "info")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": text,
        "parse_mode": "Markdown"
    }
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status == 200:
                _log("텔레그램 분석 결과 보고 전송 완료!", "ok")
            else:
                _log(f"텔레그램 전송 실패 (코드 {res.status})", "warn")
    except Exception as e:
        _log(f"텔레그램 알림 전송 오류: {e}", "warn")

def analyze_and_report():
    """최근 미디어, 댓글 및 인사이트를 분석하고 리포트를 파일로 저장한 후 텔레그램 보고 수행"""
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_file_str = datetime.now().strftime("%Y%m%d")
    
    _log("🧹 인스타그램 일일 점검 및 분석 프로세스를 시작합니다!", "step")
    
    media_list = get_media_list(limit=10)
    tg_token, tg_chat = resolve_telegram()
    
    if media_list is None:
        _log("미디어 데이터를 가져올 수 없어 분석을 중단하고 경고 보고서를 작성합니다.", "err")
        
        report_dir = os.path.join(AGENT_ROOT, "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"report_{today_file_str}.md")
        
        err_content = f"""# 📈 인스타그램 일일 분석 리포트 ({today_str}) - ⚠️ 연동 실패

본 리포트는 다다직구 인스타그램 에이전트에 의해 자동 생성되었으나 연동 오류가 발생했습니다. 🧚💦

## 🚨 API 연동 에러 안내
* **발생 일시:** {today_str}
* **원인:** Meta Graph API 토큰이 만료되었거나, 권한이 유효하지 않습니다.
* **조치 방법:**
  1. `config.md` 파일에 올바른 `META_ACCESS_TOKEN`과 `INSTAGRAM_BUSINESS_ID`가 입력되어 있는지 확인해 주세요.
  2. Meta 개발자 센터에서 새로운 시스템 사용자 액세스 토큰을 발급받아 갱신해 주셔야 합니다.
"""
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(err_content)
            _log(f"경고 리포트가 성공적으로 저장되었습니다: {report_path}", "ok")
            log_activity("ANALYZE_AND_REPORT", "FAILED_OAUTH", f"Saved warning report at {report_path}")
        except Exception as e:
            _log(f"경고 리포트 저장 실패: {e}", "err")
            
        err_msg = f"🚨 *[다다직구] 인스타그램 분석 연동 오류* 🚨\n\n날짜: {today_str}\n\nMeta Graph API 연동 실패로 인해 데이터 분석을 수행하지 못했습니다.\n`config.md` 파일의 액세스 토큰 만료 여부를 확인하고 갱신해 주세요!"
        send_telegram_notification(tg_token, tg_chat, err_msg)
        return False
        
    insights_data = get_insights()
    
    total_likes = 0
    total_comments = 0
    media_details = []
    
    for item in media_list:
        m_id = item.get("id")
        caption = item.get("caption", "(내용 없음)")
        m_type = item.get("media_type", "UNKNOWN")
        permalink = item.get("permalink", "#")
        likes = item.get("like_count", 0)
        comments_cnt = item.get("comments_count", 0)
        timestamp = item.get("timestamp", "")
        
        total_likes += likes
        total_comments += comments_cnt
        
        comments = get_comments(m_id, limit=3)
        comments_summary = []
        for c in comments:
            comments_summary.append({
                "username": c.get("username", "anonymous"),
                "text": c.get("text", "")
            })
            
        media_details.append({
            "id": m_id,
            "caption": caption,
            "type": m_type,
            "link": permalink,
            "likes": likes,
            "comments_count": comments_cnt,
            "comments": comments_summary,
            "timestamp": timestamp
        })
        
    avg_likes = total_likes / len(media_list) if media_list else 0
    avg_comments = total_comments / len(media_list) if media_list else 0
    
    report_dir = os.path.join(AGENT_ROOT, "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"report_{today_file_str}.md")
    
    report_content = f"""# 📈 인스타그램 일일 분석 리포트 ({today_str})

본 리포트는 다다직구 인스타그램 에이전트에 의해 자동으로 생성되었습니다. 🧚✨

## 📊 핵심 성과 지표 (최근 {len(media_list)}개 피드 기준)
* **총 좋아요 수:** {total_likes}개 (평균: {avg_likes:.1f}개)
* **총 댓글 수:** {total_comments}개 (평균: {avg_comments:.1f}개)
"""

    if insights_data and "data" in insights_data:
        report_content += "\n## 👥 계정 도달 및 팔로워 동향\n"
        for metric in insights_data["data"]:
            name = metric.get("name")
            values = metric.get("values", [])
            val_str = values[0].get("value", 0) if values else 0
            
            metric_label = {
                "reach": "도달 수 (Reach)",
                "follower_count": "팔로워 증가 수"
            }.get(name, name)
            
            report_content += f"* **{metric_label}:** {val_str}\n"
    else:
        report_content += "\n## 👥 계정 도달 및 팔로워 동향\n* API 연동 권한으로 인해 세부 인사이트 수집은 보류되었습니다. (피드 참여도는 정상 집계 중)\n"

    report_content += "\n## 📝 최근 게시물 상세 및 피드백 (댓글)\n"
    
    for i, m in enumerate(media_details):
        short_caption = m["caption"].replace("\n", " ")
        if len(short_caption) > 50:
            short_caption = short_caption[:50] + "..."
            
        report_content += f"""
### {i+1}. [{m['type']}] {short_caption}
* 🔗 [게시물 링크]({m['link']})
* 👍 좋아요: {m['likes']}개 | 💬 댓글: {m['comments_count']}개
* **최근 댓글:**
"""
        if m["comments"]:
            for c in m["comments"]:
                report_content += f"  - **@{c['username']}:** {c['text']}\n"
        else:
            report_content += "  - (작성된 댓글이 없습니다)\n"
            
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        _log(f"분석 리포트가 성공적으로 저장되었습니다: {report_path}", "ok")
        log_activity("ANALYZE_AND_REPORT", "SUCCESS", f"Report saved at {report_path}")
    except Exception as e:
        _log(f"리포트 파일 저장 오류: {e}", "err")
        log_activity("ANALYZE_AND_REPORT", "FAILED", f"File write error: {e}")
        
    tg_token, tg_chat = resolve_telegram()
    
    tg_summary = f"""📢 *[다다직구] 인스타그램 일일 점검 보고* 📊
날짜: {today_str}

🧚 *최근 {len(media_list)}개 피드 분석 요약*
- 총 좋아요: {total_likes}개 (평균 {avg_likes:.1f}개)
- 총 댓글수: {total_comments}개 (평균 {avg_comments:.1f}개)
"""
    if insights_data and "data" in insights_data:
        tg_summary += "\n📈 *계정 동향*"
        for metric in insights_data["data"]:
            name = metric.get("name")
            values = metric.get("values", [])
            val_str = values[0].get("value", 0) if values else 0
            metric_label = {"reach": "도달수", "follower_count": "팔로워 증가"}.get(name, name)
            tg_summary += f"\n- {metric_label}: {val_str}"
            
    tg_summary += f"\n\n📂 상세 리포트가 마크다운 파일로 저장되었습니다.\n`_agents/instagram/reports/report_{today_file_str}.md`"
    
    send_telegram_notification(tg_token, tg_chat, tg_summary)
    return True

def post_feed(image_url, caption):
    """인스타그램 피드 게시물 업로드 자동화 (2단계 처리)"""
    creds = load_config()
    token = creds["META_ACCESS_TOKEN"]
    biz_id = creds["INSTAGRAM_BUSINESS_ID"]
    
    if not token or not biz_id:
        _log("API 설정 누락 (META_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ID)", "err")
        return False
        
    _log("1단계: 미디어 아이템 업로드 컨테이너 생성 중...", "step")
    container_url = f"https://graph.facebook.com/v19.0/{biz_id}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }
    
    code, res = make_request(container_url, method="POST", data=payload)
    if code != 200:
        _log(f"미디어 컨테이너 생성 실패 (코드 {code}): {res}", "err")
        log_activity("POST_FEED_STEP1", "FAILED", f"Error: {res}")
        return False
        
    creation_id = res.get("id")
    _log(f"미디어 컨테이너 생성 완료! Container ID: {creation_id}", "ok")
    
    _log("2단계: 미디어 공식 퍼블리시(게시) 진행 중...", "step")
    publish_url = f"https://graph.facebook.com/v19.0/{biz_id}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": token
    }
    
    p_code, p_res = make_request(publish_url, method="POST", data=publish_payload)
    if p_code == 200:
        post_id = p_res.get("id")
        _log(f"인스타그램 피드 업로드 대성공! 게시글 ID: {post_id}", "ok")
        log_activity("POST_FEED", "SUCCESS", f"Post ID: {post_id}, Image: {image_url}")
        print(json.dumps(p_res, indent=2, ensure_ascii=False))
        return True
    else:
        _log(f"미디어 게시 실패 (코드 {p_code}): {p_res}", "err")
        log_activity("POST_FEED_STEP2", "FAILED", f"Error: {p_res}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Instagram Automation CLI Tool")
    parser.add_argument("--test", action="store_true", help="연동 상태 자가진단 테스트")
    parser.add_argument("--insights", action="store_true", help="참여도 및 인사이트 데이터 수집")
    parser.add_argument("--get-metrics", action="store_true", help="참여도 및 인사이트 데이터 수집 (시스템 호환용)")
    parser.add_argument("--analyze", action="store_true", help="최근 피드 내용, 인사이트, 댓글 수집 분석 및 텔레그램 보고")
    parser.add_argument("--post", action="store_true", help="새 포스팅 발행 모드")
    parser.add_argument("--image", type=str, help="포스팅할 공개 이미지 URL")
    parser.add_argument("--caption", type=str, help="포스팅 캡션 문구")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    elif args.insights or args.get_metrics:
        get_insights()
    elif args.analyze:
        analyze_and_report()
    elif args.post:
        if not args.image or not args.caption:
            _log("--post 실행을 위해선 --image와 --caption 인자가 필수입니다.", "err")
            sys.exit(1)
        post_feed(args.image, args.caption)
    else:
        parser.print_help()
