import requests
import time
import sys
import io

# 인코딩 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def test_model(model_name):
    print(f"--- Testing {model_name} ---")
    url = "http://127.0.0.1:1234/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "hello"}],
        "stream": False,
        "max_tokens": 10
    }
    
    start_time = time.time()
    try:
        r = requests.post(url, json=payload, timeout=5)
        r.raise_for_status()
        elapsed = time.time() - start_time
        print(f"SUCCESS! Time: {elapsed:.2f}s")
        print("Response:", r.json()["choices"][0]["message"]["content"].strip())
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"FAILED! Time: {elapsed:.2f}s")
        print("Error:", e)
        return False

test_model("qwen3.5-4b")
test_model("google/gemma-4-e2b")
