# DESIGN.md — AgentLab Blog Design System

Hugo Stack 테마 기반 블로그의 디자인 시스템.
이 파일은 AI 도구(Claude Code, Cursor 등)가 일관된 UI를 생성할 때 참고하는 문서다.

---

## 1. 색상 팔레트

### 테마 배경 (Stack 테마 기본값)
| 역할 | 라이트 | 다크 |
|------|--------|------|
| 페이지 배경 | `#f5f5fa` | `#303030` |
| 카드 배경 | `#ffffff` | `#424242` |
| 본문 텍스트 | `#707070` | `rgba(255,255,255,0.7)` |
| 강조 색 | `#34495e` | `#ecf0f1` |

### 인라인 SVG / 다이어그램 전용 팔레트
다크 배경(`#0f172a`) 컨테이너 안에서 사용:

| 역할 | 색상 |
|------|------|
| SVG 배경 컨테이너 | `#0f172a` |
| 일반 노드 fill | `#1e3a5f` |
| 일반 노드 stroke | `#38bdf8` |
| 일반 노드 텍스트 | `#93c5fd` |
| 강조/변경 노드 fill | `#431407` |
| 강조/변경 노드 stroke | `#f97316` |
| 강조 텍스트 | `#fb923c` |
| 성공/긍정 노드 fill | `#14432a` |
| 성공/긍정 노드 stroke | `#4ade80` |
| 성공 텍스트 | `#86efac` |
| 엣지 (기본) | `#334155` |
| 엣지 (강조, dashed) | `#f97316` |
| 단계 박스 1 (파랑) | `#1e40af` |
| 단계 박스 2 (초록) | `#065f46` |
| 단계 박스 3 (적갈) | `#7c2d12` |
| 캡션/보조 텍스트 | `#64748b` |
| 배지/수치 강조 | `#fbbf24` |
| 차트 Before (빨강) | `#ef4444` |
| 차트 After (초록) | `#22c55e` |

---

## 2. 타이포그래피

```
본문 폰트: Lato, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
코드 폰트: Menlo, Monaco, Consolas, "Courier New", monospace
```

- SVG 내 텍스트: `font-family="sans-serif"` 또는 `font-family="monospace"`
- 웹 폰트 의존 금지 (SVG에서 로드 보장 안 됨)

---

## 3. 간격 단위

| 항목 | 값 |
|------|-----|
| 카드 패딩 | `20px` (모바일), `25px` (태블릿), `30px` (데스크탑) |
| 섹션 간격 | `40px` |
| 인라인 SVG 마진 | `2rem 0` |
| SVG 컨테이너 패딩 | `1.5rem` |
| SVG 컨테이너 border-radius | `12px` |

---

## 4. 컴포넌트 패턴

### 인라인 SVG 다이어그램
```html
<div style="text-align:center; margin: 2rem 0; background:#0f172a; border-radius:12px; padding:1.5rem;">
<svg width="460" height="[높이]" viewBox="0 0 460 [높이]" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;">
  <!-- 내용 -->
</svg>
<p style="font-size:0.8rem; color:#64748b; margin-top:0.5rem;">[캡션]</p>
</div>
```

### 흐름도 (A → B → C)
- 박스: `fill="#1e40af"` → `fill="#065f46"` → `fill="#7c2d12"`, `rx="10"`
- 화살표: `stroke="#64748b"`, `stroke-width="2"`, `<marker>` defs 사용
- 텍스트: `font-size="13"`, `font-weight="bold"`, `fill="white"`, `text-anchor="middle"`

### 바 차트 (Before/After)
- Before 바: `fill="#ef4444"`, `rx="4"`
- After 바: `fill="#22c55e"`, `rx="4"`
- CSS 애니메이션 선택적으로 추가 (`animation: grow .8s .3s both`)
- 배지: `fill="#fbbf24"`, `font-size="18"`, `font-weight="bold"`

### 노드 그래프
- 일반 노드: `fill="#1e3a5f" stroke="#38bdf8" stroke-width="2"`
- 강조 노드: `fill="#431407" stroke="#f97316" stroke-width="3"`
- 성공 노드: `fill="#14432a" stroke="#4ade80" stroke-width="2"`
- 텍스트: `font-size="10" font-family="monospace" text-anchor="middle"`

---

## 5. 디자인 가이드라인

### SVG 삽입 규칙
- ❌ SMIL `<animate>` 사용 금지 → Stack 테마에서 작동 안 함
- ✅ SVG 요소는 기본 상태에서 항상 보이게 (`opacity:1`, 초기 width/height 정상값)
- ✅ CSS 애니메이션은 보조 효과로만 사용 (없어도 다이어그램이 보여야 함)
- ✅ 같은 페이지에 SVG 여러 개면 `id` 고유하게 (`id="arr1"`, `id="arr2"`)
- ✅ Hugo config에 `markup.goldmark.renderer.unsafe: true` 필요 (적용됨)

### SVG 삽입 빈도
- 포스트당 1~3개
- 흐름/단계 설명, 수치 비교, 구조 관계에서만 삽입
- 설치 방법, 장단점 섹션은 코드 블록/텍스트로 충분

### 커버 이미지
- 생성 도구: Gemini 3.1 Flash Image Preview API
- 저장 경로: `assets/images/posts/[슬러그].jpg`
- front matter: `image: images/posts/[슬러그].jpg` (앞에 `/` 붙이지 않음)

---

## 6. 파일 구조 참고

```
agentlab-blog/
├── content/post/          # 블로그 포스트 (.md)
├── assets/images/posts/   # 커버 이미지 (.jpg)
├── static/img/            # 사이트 고정 이미지 (avatar 등)
├── layouts/_partials/     # 커스텀 레이아웃
├── hugo.yaml              # Hugo 설정
└── DESIGN.md              # 이 파일
```
