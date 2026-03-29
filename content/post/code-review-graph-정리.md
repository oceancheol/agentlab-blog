---
title: "code-review-graph 정리: AI 코드리뷰를 토큰 효율적으로 만드는 방법"
date: 2026-03-29
draft: false
image: "images/posts/code-review-graph.jpg"
tags: ["code-review-graph", "Claude Code", "MCP", "코드리뷰", "AI 코딩도구"]
description: "Claude Code가 전체 코드베이스를 매번 읽는 문제를 줄이기 위해, 코드 구조를 그래프로 관리하는 code-review-graph를 초보자 관점으로 정리했다."
---

`code-review-graph`는 말 그대로 **코드 리뷰에 필요한 파일만 골라서 AI가 읽도록 만드는 도구**야.

Claude Code 같은 에이전트는 보통 작업 때 코드를 넓게 읽는 경향이 있어. 그래서 토큰이 많이 쓰이고, 핵심이 안 보이는 일이 생기기 쉬워.

이 프로젝트는 코드를 **구조적 그래프**로 만들어서, 변경 영향 범위(Blast Radius)만 전달함으로써 이를 줄이려는 목적이야.

## 왜 생겼는지

기존 방식의 문제는 단순해.

- 매번 전체 저장소를 스캔해서 느리고 토큰을 많이 씀
- 변경된 파일과 연관 파일을 사람이 일일이 찾기 어려움
- 큰 프로젝트에서 AI 응답이 비효율적

`code-review-graph`는 이런 문제를 해결하기 위해, 소스코드를 **AST(구문 트리)**로 파싱해서 **함수/클래스/임포트/호출 관계**를 노드·엣지로 만든다.

## 핵심 아이디어 한 줄

AI에게 “지금 바뀐 코드가 어떤 파일에 영향을 미치는지”만 정확히 알려주면,
AI는 더 많은 부분을 덜 읽고도 더 정확하게 리뷰할 수 있어.

<div style=”text-align:center; margin: 2rem 0;”>
<svg width=”480” height=”210” viewBox=”0 0 480 210” xmlns=”http://www.w3.org/2000/svg” style=”max-width:100%;”>
  <style>
    @keyframes crg-fade { from { opacity:0; } to { opacity:1; } }
    @keyframes crg-pulse { 0%,100% { r:26; } 50% { r:30; } }
    .crg-n  { fill:#1e293b; stroke:#38bdf8; stroke-width:1.5; opacity:0; animation:crg-fade .3s forwards; }
    .crg-nc { fill:#0f172a; stroke:#f97316; stroke-width:2.5; opacity:0; animation:crg-fade .3s .3s forwards; }
    .crg-nc-pulse { animation:crg-fade .3s .3s forwards, crg-pulse 1s 1.8s 2; }
    .crg-nl  { font:11px monospace; fill:#94a3b8; text-anchor:middle; dominant-baseline:middle; opacity:0; animation:crg-fade .3s forwards; }
    .crg-nlc { font:11px monospace; fill:#f97316; text-anchor:middle; dominant-baseline:middle; font-weight:bold; opacity:0; animation:crg-fade .3s .3s forwards; }
    .crg-e  { stroke:#334155; stroke-width:1.2; opacity:0; animation:crg-fade .3s forwards; }
    .crg-eb { stroke:#f97316; stroke-width:2; stroke-dasharray:5,3; opacity:0; animation:crg-fade .4s 2s forwards; }
    .crg-box { fill:rgba(249,115,22,0.08); stroke:#f97316; stroke-width:1; stroke-dasharray:4,2; opacity:0; animation:crg-fade .4s 2.2s forwards; }
    .crg-bt { font:10px sans-serif; fill:#f97316; text-anchor:middle; opacity:0; animation:crg-fade .4s 2.2s forwards; }
    .d1 { animation-delay:.1s; } .d2 { animation-delay:.2s; } .d3 { animation-delay:.4s; }
    .d4 { animation-delay:.5s; } .d5 { animation-delay:.7s; } .d6 { animation-delay:.9s; }
    .d7 { animation-delay:1.1s; } .d8 { animation-delay:1.3s; }
  </style>
  <!-- edges -->
  <line class=”crg-e d5” x1=”120” y1=”60” x2=”200” y2=”100”/>
  <line class=”crg-e d5” x1=”120” y1=”150” x2=”200” y2=”110”/>
  <line class=”crg-e d6” x1=”200” y1=”100” x2=”290” y2=”60”/>
  <line class=”crg-e d7” x1=”200” y1=”100” x2=”290” y2=”150”/>
  <line class=”crg-e d8” x1=”290” y1=”60” x2=”380” y2=”100”/>
  <!-- blast edges -->
  <line class=”crg-eb” x1=”200” y1=”100” x2=”290” y2=”60”/>
  <line class=”crg-eb” x1=”290” y1=”60” x2=”380” y2=”100”/>
  <!-- blast box -->
  <rect class=”crg-box” x=”265” y=”35” width=”135” height=”90” rx=”8” ry=”8”/>
  <text class=”crg-bt” x=”332” y=”22”>Blast Radius</text>
  <!-- nodes -->
  <circle class=”crg-n d1” cx=”120” cy=”60” r=”22”/>
  <text class=”crg-nl d1” x=”120” y=”60”>auth.py</text>
  <circle class=”crg-n d2” cx=”120” cy=”150” r=”22”/>
  <text class=”crg-nl d2” x=”120” y=”150”>utils.py</text>
  <circle class=”crg-nc crg-nc-pulse” cx=”200” cy=”100” r=”26”/>
  <text class=”crg-nlc” x=”200” y=”100”>api.py ✏️</text>
  <circle class=”crg-n d3” cx=”290” cy=”60” r=”22”/>
  <text class=”crg-nl d3” x=”290” y=”60”>router.py</text>
  <circle class=”crg-n d3” cx=”290” cy=”150” r=”22”/>
  <text class=”crg-nl d3” x=”290” y=”150”>models.py</text>
  <circle class=”crg-n d4” cx=”380” cy=”100” r=”22”/>
  <text class=”crg-nl d4” x=”380” y=”100”>test_api.py</text>
</svg>
<p style=”font-size:0.8rem; color:#64748b; margin-top:0.5rem;”>api.py 변경 시 영향 받는 파일만 선택 (Blast Radius)</p>
</div>

## 설치/시작은 어떻게

가장 기본 플로우는 이래.

1. `pip install code-review-graph`
2. `code-review-graph install`
3. `code-review-graph build`

`install`은 지원 툴을 자동으로 감지해서 MCP 설정을 깔아줘. Claude Code, Cursor, Windsurf, Zed, Continue, OpenCode를 지원한다는 점이 바로바로 쓸만한 부분이야.

특정 툴만 쓰면 `--platform`으로 제한 설정도 가능해.

예를 들어:
- `code-review-graph install --platform claude-code`
- `code-review-graph install --platform cursor`

초기 빌드는 500개 파일 정도라면 10초 안팎, 그다음부터는 변경분만 추적한다는 점이 실무에 좋아.

## 어떻게 동작하나

간단히 3단계야.

<div style="text-align:center; margin: 2rem 0;">
<svg width="480" height="120" viewBox="0 0 480 120" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;">
  <style>
    @keyframes stp-fade { from { opacity:0; } to { opacity:1; } }
    .stp-t { font:bold 13px sans-serif; text-anchor:middle; dominant-baseline:middle; fill:white; opacity:0; animation:stp-fade .4s forwards; }
    .stp-s { font:10px sans-serif; text-anchor:middle; dominant-baseline:middle; fill:#cbd5e1; opacity:0; animation:stp-fade .4s forwards; }
    .stp-r { opacity:0; animation:stp-fade .4s forwards; }
    .stp-a { stroke:#64748b; stroke-width:2; opacity:0; animation:stp-fade .3s forwards; marker-end:url(#sarr); }
    .sd1 { animation-delay:.2s; } .sd2 { animation-delay:.7s; } .sd3 { animation-delay:.9s; } .sd4 { animation-delay:1.4s; } .sd5 { animation-delay:1.6s; }
  </style>
  <defs>
    <marker id="sarr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="stp-r sd1" x="10" y="30" width="120" height="60" fill="#1e40af" rx="10" ry="10"/>
  <text class="stp-t sd1" x="70" y="53">① 파싱</text>
  <text class="stp-s sd1" x="70" y="70">Tree-sitter AST</text>
  <line class="stp-a sd2" x1="134" y1="60" x2="166" y2="60"/>
  <rect class="stp-r sd3" x="170" y="30" width="140" height="60" fill="#065f46" rx="10" ry="10"/>
  <text class="stp-t sd3" x="240" y="53">② 그래프 구성</text>
  <text class="stp-s sd3" x="240" y="70">노드 + 엣지</text>
  <line class="stp-a sd4" x1="314" y1="60" x2="346" y2="60"/>
  <rect class="stp-r sd5" x="350" y="30" width="120" height="60" fill="#7c2d12" rx="10" ry="10"/>
  <text class="stp-t sd5" x="410" y="53">③ 축소 전달</text>
  <text class="stp-s sd5" x="410" y="70">Blast Radius만</text>
</svg>
</div>

### 1) 파싱

코드를 Tree-sitter로 AST 파싱해서 함수/클래스/임포트 같은 단위를 노드로 만든다.

### 2) 그래프 구성

호출 관계, 의존성, 테스트 커버 같은 연결을 엣지로 붙인다.

### 3) 리뷰용 축소

변경이 생기면 그 파일의 `blast radius`를 따라 관련 호출자/의존 파일/테스트를 찾아낸다.

즉, 전체를 읽는 대신 **정말 필요한 집합**만 AI에 준다는 뜻이야.

## 실제 장점

공개된 평가 수치 기준으로는 꽤 인상적이야.

<div style="text-align:center; margin: 2rem 0;">
<svg width="400" height="130" viewBox="0 0 400 130" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;">
  <style>
    @keyframes bar-before-grow { from { width:0; } to { width:246px; } }
    @keyframes bar-after-grow  { from { width:0; } to { width:30px; } }
    @keyframes bar-fade { from { opacity:0; } to { opacity:1; } }
    .bar-lbl { font:12px sans-serif; fill:#94a3b8; }
    .bar-val { font:bold 12px sans-serif; fill:white; text-anchor:middle; dominant-baseline:middle; opacity:0; animation:bar-fade .3s forwards; }
    .badge-txt { font:bold 18px sans-serif; fill:#fbbf24; text-anchor:middle; opacity:0; animation:bar-fade .5s 2s forwards; }
    .badge-sub { font:10px sans-serif; fill:#64748b; text-anchor:middle; opacity:0; animation:bar-fade .5s 2s forwards; }
    .bv1 { animation-delay:1.1s; } .bv2 { animation-delay:1.8s; }
  </style>
  <text x="200" y="18" font-size="12" fill="#64748b" text-anchor="middle">토큰 사용량 비교</text>
  <text class="bar-lbl" x="10" y="48">Before</text>
  <rect x="75" y="33" width="246" height="22" fill="#ef4444" rx="4" ry="4" style="animation:bar-before-grow .8s .3s both;"/>
  <text class="bar-val bv1" x="198" y="44">8.2x 토큰</text>
  <text class="bar-lbl" x="10" y="93">After</text>
  <rect x="75" y="78" width="30" height="22" fill="#22c55e" rx="4" ry="4" style="animation:bar-after-grow .5s 1.3s both;"/>
  <text class="bar-val bv2" x="92" y="89">1x</text>
  <text class="badge-txt" x="330" y="65">8.2x ↓</text>
  <text class="badge-sub" x="330" y="82">절약</text>
  <text x="200" y="120" font-size="10" fill="#475569" text-anchor="middle">평균 토큰 사용량 8.2배 감소 (공식 보고 기준)</text>
</svg>
</div>

- 평균 토큰 사용량이 대체로 8.2배 줄어든 것으로 보고됨
- 영향 분석은 실제 영향을 받는 파일을 **놓치는 일 없이 100% Recall** 달성
- 2,900개 파일 정도 프로젝트도 2초 이내 증분 업데이트

단, 정밀도(precision)는 상황에 따라 낮아질 수 있어. 보수적으로 넓게 잡아서 누락은 막고, 결과적으로 읽는 파일 수가 약간 늘어나는 쪽으로 설계된 편이야.

## 한계도 분명해

- 아주 작은 단일 파일 변경은 오히려 그래프 메타데이터가 더 나올 수 있어서 비용이 비효율적으로 보일 수 있어.
- 검색 정확도는 전체적으로 좋지 않은 쪽은 아니다, 하지만 MRR이 0.35 정도로 개선 여지가 있어.
- 현재 실행 흐름 감지는 Python에서 비교적 안정적이고, JS/Go는 아직 미약한 편.

즉, “완전한 진리 엔진”이 아니라, **리뷰 효율을 올리는 보조 장치**로 보는 게 맞아.

## CLI/기능 한눈에

주로 쓸 만한 건 이런 명령들이야.

- `build` / `update`: 초기 생성과 증분 갱신
- `status`: 그래프 상태 확인
- `watch`: 파일 변경 시 자동 갱신
- `review-delta`, `review-pr`, `detect-changes`: 변경 리뷰용 워크플로
- `visualize`, `wiki`: 그래프 기반 구조/위키 생성
- `/code-review-graph:review-delta`, `/code-review-graph:review-pr` 같은 슬래시 커맨드

그리고 MCP 툴 레벨로는 impact 분석, 구조 쿼리, 검색, 리팩토링 추천까지 붙어 있어서, 단순 “한 번 실행하고 끝”보다 확장성이 커.

## 어떤 팀에 잘 맞나

이런 팀에서 특히 유용해.

- 코드 리뷰 빈도가 높고 변경 범위가 커서 노이즈가 많을 때
- Claude/Cursor/다른 AI 툴을 자주 쓰는 팀
- 대규모 저장소에서 리뷰 품질을 일정하게 유지하고 싶은 곳
- 멀티 레포를 묶어서 점진적으로 운영하려는 조직

반대로, 변경이 아주 작고 소형 프로젝트만 다룬다면 비용 대비 체감이 적을 수 있어.

## 한 줄 요약

`code-review-graph`는 코드베이스를 구조 그래프로 바꿔서, AI가 관련 있는 코드만 읽게 만들어
토큰 낭비를 줄이고 리뷰 효율을 올리는 툴셋이야.

## 핵심 포인트

- AI가 전체를 읽는 대신 영향권 중심으로 읽게 만든다.
- Python/JS/TS, Go, Rust, Java 등 18개 언어 지원.
- 증분 업데이트가 빠르다(2초 이하 목표).
- 정밀도보다 누락 회피를 우선한 보수적 분석 특성.
- Slash command + MCP 통합으로 워크플로에 바로 넣기 좋다.

---

*이 글은 `tirth8205/code-review-graph` 공개 자료를 초보자 관점으로 정리한 블로그 요약이다.*
