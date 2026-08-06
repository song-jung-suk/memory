#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
중국 구매셀러 50명 데이터 수집 스크립트
통관 비용/자격증명 필터링 자동화

[근거: 의사결정 로그 — 2026-06-14T12-42, 2026-06-13T09-23]
"""

import pandas as pd
import requests
from datetime import datetime
import os

# 경로 설정
OUTPUT_PATH = r"E:\work\_company\sessions\2026-06-20T14-XX/seller_db_v1.csv"
TARGET_COUNT = 50
CUTOFF_CUSTOMS = 30  # 통관비 기준 (원)

# 데이터 수집 함수
def collect_seller_list():
    """타오바오/1688 셀러 리스트 수집"""
    print(f"[{datetime.now()}] 셀러 리스트 수집 시작...")
    
    # 타오바오 셀러 디렉토리 스캔
    sellers = []
    for seller_id in range(1, 50):
        try:
            # 실제 API 호출 (OAuth 필요)
            url = f"https://taobao.com/api/v3/seller/{seller_id}"
            response = requests.get(url)
            if response.status_code == 200:
                seller_info = extract_seller_data(response.json())
                sellers.append(seller_info)
        except Exception as e:
            print(f"Error {seller_id}: {e}")
    
    return sellers

def filter_by_customs_cost(sellers):
    """통관 비용 30% 이하 필터링"""
    filtered = []
    for seller in sellers:
        if seller['customs_fee'] <= CUTOFF_CUSTOMS * 1.2:
            filtered.append(seller)
    
    print(f"[{datetime.now()}] 통관비 기준 필터링 완료: {len(filtered)}명")
    return filtered

def filter_by_qualification(sellers):
    """자격증명 요구사항 추출"""
    qualified = []
    for seller in sellers:
        qualification_type = seller['qualification']
        if 'KC 인증' not in str(qualification_type) or '선택' == str(qualification_type):
            qualified.append(seller)
    
    print(f"[{datetime.now()}] 자격증명 필터링 완료: {len(qualified)}명")
    return qualified

def save_to_csv(data, path=OUTPUT_PATH):
    """CSV 파일 저장"""
    df = pd.DataFrame(data)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print(f"[{datetime.now()}] 데이터베이스 저장: {path}")

if __name__ == "__main__":
    print("="*60)
    print("🔍 중국 구매셀러 50명 데이터 수집 시작")
    print("="*60)
    
    # 1. 셀러 리스트 수집
    sellers = collect_seller_list()
    
    # 2. 통관 비용 필터링
    filtered = filter_by_customs_cost(sellers)
    
    # 3. 자격증명 필터링
    qualified = filter_by_qualification(filtered)
    
    # 4. 저장
    save_to_csv(qualified, OUTPUT_PATH.replace('XX', datetime.now().strftime('%H-%M')))
    
    print("="*60)
    print(f"✅ 완료: {len(qualified)}명 데이터베이스 구축")
    print("="*60)