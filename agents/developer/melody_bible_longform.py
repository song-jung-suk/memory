import os
import sys
import json
import io

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def generate_long_form_plan():
    print("=== [멜로디 성경] 3시간/8시간 롱버전 VOD 패키지 기획안 생성 ===")
    
    top_tracks = [
        "1. 아침기도 (시편 18편 36절) - 실족하지 않는 넓은 길",
        "2. 부활주일/고난주간 아침기도",
        "3. 주일 아침기도 (요한복음 4장 24절) - 영과 진리로 예배",
        "4. 아침기도 (시편 18편 2절) - 내 인생의 견고한 요새, 반석",
        "5. 아침기도 (시편 122편 7절) - 우리 가정의 평강과 형통",
        "6. 부르짖는 자의 간구 (시편 27편 7절)",
        "7. 나를 푸른 초장으로 인도하시는 선한 목자 (시편 23편)",
        "8. 환난 중에도 흔들리지 않는 평안 (시편 27편 5절)"
    ]
    
    plan = {
        "title": "🌙 [8시간 연속재생] 잠 못 드는 밤, 마음을 가라앉히는 깊은 수면 성경 찬양 모음집",
        "description": "너무 힘들도 마음이 무거울 때, 주님의 평안 안에서 고요히 잠드는 8시간 수면 찬양입니다.\n\n" +
                       "📌 [트랙리스트 / 타임스탬프]\n" + "\n".join([f"00:{i*15:02d}:00 - {t}" for i, t in enumerate(top_tracks)]) +
                       "\n\n#수면찬양 #성경묵상 #시편기도 #멜로디성경 #8시간연속재생",
        "tags": ["수면찬양", "8시간찬양", "성경묵상", "시편기도", "수면음악", "멜로디성경", "아침기도"]
    }
    
    print("\n✅ 기획안 생성 완료:")
    print("제목:", plan["title"])
    print("\n설명란 미리보기:\n", plan["description"][:300] + "...")
    
if __name__ == "__main__":
    generate_long_form_plan()
