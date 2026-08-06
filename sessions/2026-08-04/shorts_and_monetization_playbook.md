# 🚀 쇼츠 자동화 & 수익화 실전 가이드북 (Practitioner's Playbook)

이 가이드북은 옵시디언 저장소(`E:\Obsidian Vault`)에 수집된 490여 개의 핵심 노트 중 **쇼츠 자동화**, **캐릭터 일관성 유화 프롬프트**, **애드센스 & N잡 수익화 팁**을 집약하여 즉시 실행할 수 있도록 정리한 실전 지침서입니다.

---

## 1. 🎬 AI 쇼츠 생성 & 캐릭터 일관성 프롬프트 (VEO 3.1 & Google Flow)

### 📌 캐릭터 얼굴 일관성 문제 99% 해결법 (Whisk / VEO 3.1)
AI 영상 및 이미지 생성 시 장면마다 얼굴이 바뀌는 문제를 방지하려면 **'캐릭터 시트(Character Sheet)'** 프롬프트를 먼저 작성해야 합니다.

#### 1) 캐릭터 시트 마스터 프롬프트 (Whisk / Nano Banana / Gemini)
```text
[Character Sheet]
- Subject: A 25-year-old Korean female tech influencer with short black bob hair, wearing a sleek minimalist white hoodie and transparent rim glasses.
- Views: Front view, 45-degree side view, back view, close-up face portrait, full body standing pose.
- Style: Hyper-realistic 3D render, Pixar cinematic lighting, vibrant pastel background, 8k resolution.
- Consistency Tag: #Char_TechGirl_2026
```

#### 2) 역프롬프트(Reverse Prompting) 꿀팁
- 떡상한 해외 AI 영상이나 이미지를 발견하면 **"이 이미지/영상의 디테일한 카메라 앵글, 조명, 화풍을 역추출해 줘"** 프롬프트를 Gemini/Qwen에게 주어 동일 스타일 프롬프트를 복제합니다.

---

## 2. ⚡ 캡컷(CapCut) & 자막/오디오 자동 편집 3분 루틴

1. **대본 자동 템플릿**: 대본 텍스트만 준비해 캡컷 자동 캡션(Auto Caption)에 넣으면 1초 만에 텍스트 마스크 및 폰트 효과가 들어갑니다.
2. **오디오 파형(Spectrum Audio) 연출**:
   - 캡컷 오디오 파형 효과 사용 -> 네온 핑크/시안 파형 선택 -> 키프레임 마스크 적용으로 영상 하단 배치.
3. **후킹 인트로 2초 법칙**:
   - 첫 2초 이내에 텍스트 인트로 효과(시네마틱 줌 / 텍스트 뒤 등장 효과)와 강력한 효과음(Whoosh / Swoosh)을 배치하여 시청 지속 시간을 극대화합니다.

---

## 3. 📈 애드센스 & 스레드(Threads) 수익화 쾌속 팁

### 💡 애드센스 승인 "가치가 별로 없는 콘텐츠" 탈출 공식
1. **글자 수**: 최소 1,500자 이상 / H2, H3 소제목 3개 이상 배치
2. **이미지 카테고리**: 본문에 이미지 1~2개 배치하되, 반드시 **`alt` 태그(대체 텍스트)**에 키워드 포함
3. **가독성 세팅**: 불필요한 서론 제거, 결론에 **3줄 요약 표(Table)** 삽입

### 📱 스레드(Threads) + 쿠팡파트너스 100% 자동화 원리
1. **이슈/썰 원고 추출**: 네이버 지식iN / 커뮤니티 인기글을 로컬 LLM(Qwen/Gemma4)으로 '스레드 톤앤매너'로 요약
2. **댓글 링크 전략**: 본문에는 쿠팡 파트너스/제휴 링크를 걸지 않고, **첫 번째 댓글에 제휴 링크 배치**하여 계정 제제(Shadowban) 방지.

---

## 🛠️ 에이전트 연동 실행 가이드 (Qwen 3.5 / Gemma 4 / Antigravity)

현재 PC에 세팅된 **LM Studio (Qwen 3.5 / Gemma 4)**와 **구글 안티그래비티**를 연동할 때의 역할 분담:

- **LM Studio (Qwen 3.5 / Gemma 4 - API 비용 0원)**:
  - 스레드용 원고 요약, 유튜브 대본 텍스트 교정, 키워드 추출, 카테고리 분류
- **Google Antigravity (Gemini Free Tier API)**:
  - 캡컷 편집용 스크립트 작성, 웹 크롤링 분석, 옵시디언 파일 관리 및 구조화
