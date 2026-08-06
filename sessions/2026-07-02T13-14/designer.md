# 🎨 Designer — 블로그 게시글과 쇼츠 영상 썸네일 통일된 Red/Red-Grey 컬러 팔레트 적용, 브랜드 가이드에 맞춰 1080x1920 비율로 썸네일 시각 가이드 및 웹 페이지 CTA 버튼 디자인 제공



🎨 Designer: 작업 시작합니다.

---

## 📋 우선순위 3 가지 작업 결정 및 분배

| 순위 | 작업 | 에이전트 | 설명 |
|---|---|---|---|
| **1** | 블로그 포스트 + 쇼츠 썸네일 통일된 Red/Red-Grey 컬러 팔레트 적용 | 🎨 Designer (본인) | 브랜드 가이드에 맞춰 1080x1920 비율로 시각 가이드 생성 |
| **2** | 웹 페이지 CTA 버튼 디자인 및 색상 코드 제공 | 🎨 Designer (본인) | 웹 전환율 극대화 위한 Red/Grey CTA 버튼 설계 |
| **3** | 모닝 브리핑 후 24 시간 내 실행 완료 보고 | 📊 레오 (Writer) | 실행 상태 모니터링 및 결과 분석 |

---

## 🎨 산출물: 통일된 Red/Red-Grey 컬러 시스템 및 디자인 가이드

### `sessions/2026-07-02T13-45/designer_visual_system_guide.md` 생성 완료

```markdown
# 🏢 다다직구 — 브랜드 시각 가이드 (Unified Visual System)

## 1. 브랜드 컬러 팔레트: Red/Red-Grey System

### 🎨 메인 컬러 코드

| 용도 | 색상명 | HEX | RGB | 사용 비율 |
|---|---|---|---|---|
| **Primary** | Crimson Red (주톤) | `#DC143C` | rgb(220, 20, 60) | 70% |
| **Secondary** | Dark Grey (배경/서브) | `#2B2B2B` | rgb(43, 43, 43) | 15% |
| **Accent** | Light Red-Grey (고조) | `#C04865` | rgb(192, 72, 101) | 10% |
| **Text** | White (대비 텍스트) | `#FFFFFF` | rgb(255, 255, 255) | 3% |

### 🎨 색상 적용 규칙

- **YouTube 썸네일**: Primary Red + Light Red-Grey 배경, 흰색 텍스트
- **블로그 포스트**: Secondary Grey 배경 + Primary Red CTA 버튼
- **웹 페이지**: Grey 영역에서 Primary Red 버튼 강조

---

## 2. YouTube 썸네일 시각 가이드 (1080x1920)

### 🖼️ 썸네일 템플릿 구조

```markdown
# 📐 YouTube Shorts Thumbnail Template (1080×1920 px)

## A. 레이어 구성
| 레이어 | 색상 | 용도 |
|---|---|---|
| 배경 | `#DC143C` (Primary Red, 50% 불투명) | 혼돈/행동 유도 |
| 텍스트 영역 | 흰색 (`#FFFFFF`) + Black (`#2B2B2B` 반투명) | CTR 극대화 대비 |
| 화살표 요소 | `#DC143C` → `#00E676` (초록) | 중국→한국 흐름 표현 |

## B. 폰트 가이드
- **Main Title**: Impact Bold, 72pt, White
- **Subtitle**: Roboto Medium, 36pt, White
- **Accent**: Crimson Red (#DC143C) for arrows/icons

## C. 예시 썸네일 구성 (애드센스 승인 콘텐츠)

```
┌─────────────────────────────────────┐
│ [Primary Red Background]             │
│                                     │
│  ✅ 애드센스 승인!                   │
│         (White Bold Text, Centered)│
│                                     │
│  🇨🇳 → 🇰🇷                          │
│  (Crimson Arrow Icon)                │
│                                     │
│  [중국 소싱]                         │
│         (Grey Subtitle)              │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. 블로그 포스트 CTA 디자인 가이드

### 📝 블로그 CTA 버튼 스타일

```markdown
# 🔗 Blog Post CTA Button Style

## HTML 코드 예시
```css
.cta-button {
    background: linear-gradient(90deg, #DC143C 0%, #C04865 100%);
    color: #FFFFFF;
    padding: 16px 32px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.3s ease;
}

.cta-button:hover {
    background: linear-gradient(90deg, #C04865 0%, #DC143C 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(220, 20, 60, 0.4);
}
```

## 사용 위치
- 블로그 글 마지막 문단 (CTA 문구 포함)
- 관련 제품/서비스 링크 삽입 시
</br>
```html
<a href="https://your-link.com" class="cta-button">월 100 만 원 달성하기</a>
```

---

## 4. 웹 페이지 전환율 최적화 (LTV 기반 CTA)

### 📊 CTA 버튼 배치 전략

| 위치 | 목적 | 색상 |
|---|---|---|
| Header | 브랜드 인지도 + 신뢰도 | Grey + Primary Red Accent |
| Hero Section | 초기 전환 유도 | Full Primary Red |
| Feature Card | 가치 제시 후 유도 | Grey Background + Red CTA |
| Footer | 마지막 기회 제공 | Grey + White Text |

### 📈 예상 전환율 목표

- **CTR (클릭률)**: 3.5% 이상
- **LTV 기반**: 월 100 만 원 달성 고객수 420 명
- **CTA 배치**: 랜딩 페이지 3 위치 (Hero, Feature, Footer)

---

## 📝 다음 단계: <Designer 에이전트 — 시각 가이드 및 CTA 디자인 파일 생성 완료>
