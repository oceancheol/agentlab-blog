---
title: "ClawSweeper 정리: 이슈와 PR을 보수적으로 정리하는 유지보수 봇"
date: 2026-04-28T13:49:50+09:00
draft: false
tags: ["ClawSweeper", "OpenClaw", "GitHub", "유지보수", "AI 에이전트", "오픈소스"]
description: "ClawSweeper가 무엇인지, 왜 함부로 닫지 않는 보수적 유지보수 봇인지, 그리고 OpenClaw 저장소에서 어떻게 이슈와 PR을 관리하는지 정리한 글이다."
image: images/posts/clawsweeper-정리.jpg
---

`ClawSweeper`는 OpenClaw 쪽 저장소에서 **열린 이슈와 PR을 주기적으로 검토하고, 정말 닫아도 되는 항목만 조심스럽게 정리하는 유지보수 봇**이야.

이 프로젝트가 흥미로운 이유는 단순히 “이슈를 자동으로 닫는 봇”이 아니기 때문이야. 오히려 반대에 가까워. 기본 태도는 **가능하면 열어두고, 증거가 충분할 때만 정리한다**는 쪽이야. 그래서 운영 철학이 꽤 선명하다.

현재 README 기준으로 ClawSweeper는 `openclaw/openclaw`와 `openclaw/clawhub`를 대상으로 동작하고, 각 이슈나 PR마다 **마크다운 보고서**를 남기고 필요할 때만 **지속형 리뷰 코멘트**를 갱신해.

## 한 줄로 보면 어떤 도구인가

ClawSweeper는 이렇게 이해하면 쉬워.

- 저장소의 열린 이슈와 PR을 주기적으로 훑고
- 각 항목마다 판단 근거를 기록하고
- 닫아도 된다는 결론이 나와도 바로 닫지 않고
- 별도 적용 단계에서 한 번 더 확인한 뒤 반영하는 봇

즉, 핵심은 자동화 자체보다 **자동화의 신중함**에 있어.

## 왜 눈에 띄나

오픈소스 저장소가 커질수록 이슈와 PR은 계속 쌓여. 문제는 쌓이는 양보다도, 그 안에 섞이는 상태가 너무 다양하다는 거야.

- 이미 해결됐는데 남아 있는 이슈
- 실제로는 재현되지 않는 버그 리포트
- 다른 저장소에서 다루는 게 맞는 요청
- 중복 이슈
- 정보가 너무 적어서 처리할 수 없는 리포트
- 오래됐지만 다시 검토할 가치가 애매한 항목

대부분의 자동 정리 봇은 여기서 공격적으로 움직이다가 신뢰를 잃기 쉬워. 그런데 ClawSweeper는 반대로 **닫는 기준을 강하게 제한**해. README에서 close 제안을 허용하는 조건도 꽤 좁다.

- 현재 `main`에 이미 구현돼 있음
- 현재 `main`에서 재현되지 않음
- core가 아니라 ClawHub 스킬/플러그인 쪽이 더 적절함
- 중복되었거나 더 대표적인 이슈/PR로 대체됨
- 구체적이긴 하지만 이 저장소에서 액션할 수 없음
- 내용이 너무 불명확해서 조치가 불가능함
- 60일 이상 지난 stale 이슈인데 검증할 정보가 부족함

이 보수성이 이 프로젝트의 가장 큰 특징이야.

## 구조는 세 단계로 나뉜다

ClawSweeper 구조는 크게 **Scheduler**, **Review Lane**, **Apply Lane**으로 나뉘어 있어.

<div style="background:#0f172a; border-radius:12px; padding:1.5rem; margin:1.5rem 0;">
<svg viewBox="0 0 860 180" width="100%" role="img" aria-label="ClawSweeper workflow diagram">
  <defs>
    <marker id="cw-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#94a3b8"></path>
    </marker>
  </defs>
  <rect x="30" y="45" width="220" height="90" rx="18" fill="#1e293b" stroke="#38bdf8" stroke-width="2"></rect>
  <rect x="320" y="45" width="220" height="90" rx="18" fill="#1e293b" stroke="#a78bfa" stroke-width="2"></rect>
  <rect x="610" y="45" width="220" height="90" rx="18" fill="#1e293b" stroke="#34d399" stroke-width="2"></rect>
  <text x="140" y="78" text-anchor="middle" fill="#e2e8f0" font-size="24" font-weight="700">Scheduler</text>
  <text x="140" y="106" text-anchor="middle" fill="#cbd5e1" font-size="15">무엇을 언제 볼지 결정</text>
  <text x="430" y="78" text-anchor="middle" fill="#e2e8f0" font-size="24" font-weight="700">Review Lane</text>
  <text x="430" y="106" text-anchor="middle" fill="#cbd5e1" font-size="15">근거 수집, 보고서 작성,</text>
  <text x="430" y="126" text-anchor="middle" fill="#cbd5e1" font-size="15">close 제안까지만 수행</text>
  <text x="720" y="78" text-anchor="middle" fill="#e2e8f0" font-size="24" font-weight="700">Apply Lane</text>
  <text x="720" y="106" text-anchor="middle" fill="#cbd5e1" font-size="15">상태 재검증 뒤</text>
  <text x="720" y="126" text-anchor="middle" fill="#cbd5e1" font-size="15">실제 코멘트/종료 반영</text>
  <line x1="250" y1="90" x2="320" y2="90" stroke="#94a3b8" stroke-width="4" marker-end="url(#cw-arrow)"></line>
  <line x1="540" y1="90" x2="610" y2="90" stroke="#94a3b8" stroke-width="4" marker-end="url(#cw-arrow)"></line>
</svg>
</div>

### 1) Scheduler

스케줄러는 어떤 항목을 얼마나 자주 볼지 정해.

README 기준으로 보면,

- 새롭거나 최근 활동이 있는 항목은 더 자주 보고
- PR과 생성 30일 이내 이슈는 매일 보고
- 오래되고 조용한 이슈는 주간 cadence로 내려가고
- apply 단계는 15분마다 깨어나되 할 일이 없으면 빠르게 종료해

여기서 중요한 건 단순 반복 스캔이 아니라 **활동성과 연령에 따라 점검 빈도를 나눈다**는 점이야.

### 2) Review Lane

리뷰 단계는 제안만 해. 실제 종료는 하지 않아.

이 단계에서 하는 일은 대략 이래.

- 열린 이슈와 PR을 스캔해서 배치 구성
- 대상 저장소의 `main` 기준으로 상태 확인
- Codex 모델로 검토 수행
- 각 항목을 `records/<repo>/items/<번호>.md` 형태의 보고서로 저장
- 판단 결과와 근거, 코멘트 초안, 메타데이터를 기록

즉, 사람 리뷰어가 남길 만한 흔적을 **파일 기반으로 평평하게 남긴다**는 점이 인상적이야. 나중에 왜 그런 판단이 나왔는지 추적하기도 쉽고, 자동화가 어설프게 블랙박스처럼 느껴지지도 않아.

### 3) Apply Lane

실제 GitHub에 반영하는 건 apply 단계야.

이 단계는 이미 생성된 보고서를 읽고, 그 판단이 **지금도 여전히 유효한지 다시 확인한 뒤**에만 움직여. 예를 들어,

- 스냅샷이 바뀌지 않았는지
- 라벨 상태가 안전한지
- 메인테이너 작성 항목이 아닌지
- 봇 자신의 리뷰 코멘트 외에 상태 변화가 없는지

같은 걸 다시 점검해.

이 설계 덕분에 review에서 한 번, apply에서 한 번, 사실상 **이중 안전장치**가 걸려 있는 셈이야.

## 안전장치가 꽤 강하다

ClawSweeper를 그냥 “청소 봇”으로 보면 놓치기 쉬운 부분이 바로 이 안전 설계야.

README에서 특히 눈에 띄는 원칙은 이거야.

- **메인테이너가 만든 항목은 자동 종료하지 않음**
- 보호 라벨이 있으면 close 제안을 막음
- PR이 `Fixes #123` 같은 문법으로 이슈를 닫도록 연결돼 있으면 함부로 종료하지 않음
- 같은 작성자의 이슈/PR 쌍은 한쪽만 섣불리 닫지 않음
- 리뷰 단계에서는 GitHub write 토큰 없이 동작함
- 실제 close 직전에도 GitHub 상태를 다시 확인함

이런 제약은 속도를 늦추지만, 유지보수 봇의 신뢰를 높여. 특히 대형 저장소일수록 “빨리 정리하는 능력”보다 **잘못 닫지 않는 능력**이 더 중요할 때가 많아.

## 대시보드가 운영 감각을 보여준다

ClawSweeper README는 단순 소개 문서가 아니라 **실시간 운영 보드** 역할도 해.

2026년 4월 28일 기준 공개된 대시보드를 보면,

- 최근 24시간 동안 2233건 리뷰
- close 결정 115건
- keep-open 결정 2118건
- comments synced 1101건
- apply skip 15건

이라는 식으로 꽤 상세한 운영 지표를 보여줘.

이 숫자에서 읽히는 건 분명해. 이 봇은 “많이 닫는 봇”이 아니라, **대부분을 열어둔 채 검토 흔적을 남기는 봇**이야. 실제로 keep-open 결정이 압도적으로 많다.

그게 오히려 건강한 신호라고 봐. 대형 저장소의 자동화는 공격성보다 보수성이 더 중요하니까.

## 파일 기반 기록이 특히 좋다

개인적으로 이 프로젝트에서 제일 마음에 드는 부분은 **항목별 마크다운 기록**이야.

자동화 시스템은 종종 판단을 내부 상태에만 묻어버려. 그러면 나중에 보면 “왜 이 이슈가 닫혔지?” 같은 질문에 답하기 어려워져. 반면 ClawSweeper는 항목별 보고서를 남기니까,

- 판단 이유를 사람이 읽을 수 있고
- 후속 감사가 가능하고
- 잘못된 판단이 나와도 수정 지점이 명확하고
- 자동화와 사람 운영이 자연스럽게 섞여

결국 이건 단순한 봇이 아니라, **유지보수 의사결정을 문서화하는 시스템**에 더 가까워 보여.

## 이런 팀에 특히 잘 맞을 것 같아

ClawSweeper 같은 도구는 아무 저장소나 동일하게 잘 맞는 타입은 아니야. 특히 아래 같은 환경에서 가치가 커 보여.

- 이슈와 PR 양이 많아서 사람이 전부 순회하기 어려운 팀
- 자동 종료는 하고 싶지만 신뢰 문제 때문에 조심스러운 팀
- “왜 닫았는지”를 문서로 남기고 싶은 팀
- 코멘트, close, 감사 기록을 분리된 단계로 운영하고 싶은 팀

반대로 작은 저장소에서는 이 정도 구조가 다소 무겁게 느껴질 수도 있어. 하지만 규모가 커질수록 이런 보수적 자동화는 꽤 설득력이 생긴다.

## 마무리

ClawSweeper는 겉으로 보면 이슈 정리 봇이지만, 실제로는 **오픈소스 유지보수에서 자동화가 어디까지 개입해야 하는지 꽤 신중하게 설계한 프로젝트**야.

핵심은 간단해.

- 닫는 자동화보다 **근거 중심 검토 자동화**에 가깝고
- 빠른 정리보다 **안전한 정리**를 우선하고
- 결과보다 **판단 기록**을 중요하게 본다

이런 방향은 앞으로 유지보수 봇을 설계할 때 꽤 좋은 기준점이 될 수 있어. “무엇을 자동화할까”보다 “무엇을 자동화하지 말아야 할까”를 먼저 정한 프로젝트처럼 보여서 더 인상적이야.

원본 저장소: <https://github.com/openclaw/clawsweeper>
