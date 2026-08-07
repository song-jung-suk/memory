# -*- coding: utf-8 -*-
"""
Session Logger Utility
E:\work\sessions 디렉토리에 에이전트 작업 결과물 및 리포트를
날짜/시간별 세션 폴더 및 latest 디렉터리에 자동으로 통합 보관합니다.
"""
import os
import sys
import shutil
import datetime
import io

# Windows 콘솔 인코딩 방지
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

SESSIONS_DIR = r"E:\work\sessions"

def get_current_session_dir():
    """현재 시각 기준 세션 폴더 경로 반환 (예: E:\work\sessions\2026-08-06T22-45)"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M")
    session_path = os.path.join(SESSIONS_DIR, now_str)
    os.makedirs(session_path, exist_ok=True)
    return session_path

def save_session_artifact(agent_name, filename, content):
    """
    특정 에이전트의 산출물을 현재 세션 디렉터리와 latest 디렉터리에 동시 보관
    :param agent_name: 에이전트명 (예: 'youtube', 'writer', 'instagram', 'developer')
    :param filename: 저장할 파일 이름 (예: 'report.md', 'wordpress_post.md')
    :param content: 보관할 마크다운 또는 텍스트 내용
    :return: 저장된 파일의 전체 경로
    """
    session_dir = get_current_session_dir()
    
    # 1. 세션 폴더 내 저장 (파일명 중복 방지 옵션)
    if not filename.endswith('.md') and not filename.endswith('.txt') and not filename.endswith('.json'):
        filename += '.md'
        
    session_file_path = os.path.join(session_dir, f"{agent_name}_{filename}") if not filename.startswith(agent_name) else os.path.join(session_dir, filename)
    
    with open(session_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    # 2. latest 디렉터리에 복사/갱신
    latest_dir = os.path.join(SESSIONS_DIR, "latest")
    os.makedirs(latest_dir, exist_ok=True)
    
    latest_file_name = os.path.basename(session_file_path)
    latest_file_path = os.path.join(latest_dir, latest_file_name)
    
    with open(latest_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    # 3. 최신 통합 요약 로그 파일 (latest_summary.md) 갱신/추가
    summary_path = os.path.join(latest_dir, "latest_summary.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry = f"\n\n--- \n### 📌 [{timestamp}] 에이전트: {agent_name} | 파일: {latest_file_name}\n\n{content}\n"
    
    mode = 'a' if os.path.exists(summary_path) else 'w'
    with open(summary_path, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write("# 📋 Connect AI 최신 에이전트 산출물 통합 요약\n")
        f.write(entry)
        
    print(f"💾 [SessionLogger] 산출물 저장 완료: {session_file_path}")
    return session_file_path

if __name__ == "__main__":
    # 유틸리티 작동 테스트
    test_path = save_session_artifact("test_agent", "test_report.md", "# 테스트 산출물\n성공적으로 E:\\work\\sessions 에 보관되었습니다.")
    print(f"테스트 완료: {test_path}")
