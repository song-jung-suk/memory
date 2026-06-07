import socket
import requests
import json
import os

def check_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

print(f"Ollama 포트(11434) 오픈 여부: {check_port('127.0.0.1', 11434)}")
print(f"LM Studio 포트(1234) 오픈 여부: {check_port('127.0.0.1', 1234)}")

# LM Studio API 응답 테스트
if check_port('127.0.0.1', 1234):
    try:
        r = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        print("LM Studio /v1/models 응답 성공!")
        print("모델 목록:", [m["id"] for m in r.json().get("data", [])])
    except Exception as e:
        print("LM Studio API 요청 실패:", e)

# Ollama API 응답 테스트
if check_port('127.0.0.1', 11434):
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        print("Ollama /api/tags 응답 성공!")
        print("모델 목록:", [m["name"] for m in r.json().get("models", [])])
    except Exception as e:
        print("Ollama API 요청 실패:", e)
