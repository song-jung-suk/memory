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
AGENT_ROOT = os.path.dirname(HERE)
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
    
    if not token or not biz_id:
        _log("META_ACCESS_TOKEN 또는 INSTAGRAM_BUSINESS_ID가 비어 있습니다. config.md를 먼저 채워주세요.", "warn")
        return False
        
    # Meta Graph API 호출
    url = f"https://graph.facebook.com/v19.0/{biz_id}?fields=username,name,biography,followers_count,media_count&access_token={token}"
    code, res = make_request(url)
    
    if code == 200:
        _log(f"인스타그램 연동 확인 성공! 계정명: @{res.get('username')}", "ok")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        log_activity("TEST_CONNECTION", "SUCCESS", f"Account: @{res.get('username')}")
        return True
    else:
        _log(f"인스타그램 연동 실패 (코드 {code}): {res}", "err")
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
        
    # 도달(reach), 참여(impressions), 프로필 뷰(profile_views) 수집
    metrics = "impressions,reach,profile_views"
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
    parser.add_argument("--post", action="store_true", help="새 포스팅 발행 모드")
    parser.add_argument("--image", type=str, help="포스팅할 공개 이미지 URL")
    parser.add_argument("--caption", type=str, help="포스팅 캡션 문구")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    elif args.insights:
        get_insights()
    elif args.post:
        if not args.image or not args.caption:
            _log("--post 실행을 위해선 --image와 --caption 인자가 필수입니다.", "err")
            sys.exit(1)
        post_feed(args.image, args.caption)
    else:
        parser.print_help()
