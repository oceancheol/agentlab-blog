---
title: "Claude Code용 Codex 플러그인 정리: 코드 리뷰와 작업 위임을 한 번에"
date: 2026-03-31
draft: false
image: "images/posts/claude-code-codex-plugin.jpg"
tags: ["Claude Code", "Codex", "코드 리뷰", "MCP", "개발 도구"]
description: "OpenAI Codex 플러그인이 Claude Code에서 코드 리뷰/작업 위임을 어떻게 동작시키는지, 언제 쓰면 좋은지 초보자도 바로 쓸 수 있게 정리했다."
---

`openai/codex-plugin-cc`는 Claude Code 안에서 **Codex를 호출**해 코드 리뷰와 작업 위임을 쉽게 하게 만든 플러그인이다.

핵심은 간단해. 지금까지 별도 창에서 Codex를 돌리던 걸, 지금 쓰는 Claude Code 흐름 안으로 가져온다는 점이야.

## 한 줄 요약

이 플러그인은 현재 작업 브랜치나 변경분을 Codex가 읽고, 리뷰/수정 제안까지 할 수 있게 하는 도구다.

단, 기본 동작은 로컬 환경의 Codex CLI를 그대로 사용한다는 점이 핵심이야.

![Codex 플러그인 핵심 흐름](/images/posts/claude-code-codex-flow.jpg)

## 어떤 기능이 있나

플러그인에서 제공하는 명령은 크게 4개 축이야.

- `/codex:review`
  - 현재 변경분 읽기 전용 리뷰
  - `--base main`처럼 기준 브랜치를 지정해 비교 가능
  - `--background`로 백그라운드 실행 가능
- `/codex:adversarial-review`
  - 단순 버그 찾기보다 설계 판단까지 도전적으로 리뷰
  - 안전성·트레이드오프·장애 위험 같은 리스크를 짚어주는 용도
- `/codex:rescue`
  - Codex에게 문제 해결 작업을 위임
  - 버그 원인 분석, 패치 제안, 이어서 처리 같은 실무적 작업에 활용
- `/codex:status`, `/codex:result`, `/codex:cancel`
  - 백그라운드 작업 조회/결과 확인/취소를 관리

그 밖에 `/codex:setup`은 설치 상태와 인증, 그리고 선택 기능인 review gate를 다루는 설정 명령이야.

## 설치/시작은 이렇게

요약하면 4단계다.

1. 플러그인 마켓플레이스 등록
2. 플러그인 설치
3. 플러그인 리로드
4. `/codex:setup`으로 준비 상태 점검

대충 이렇게 적으면 돼.

```bash
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

`/codex:setup`에서 Codex 미설치가 감지되면 안내로 설치를 유도하기도 해.

원하면 직접 설치도 가능해.

```bash
npm install -g @openai/codex
```

## 추천 사용 시나리오

### 1) 리뷰 게이트 전 단계 점검

큰 변경 직전에 `/codex:review`로 먼저 돌려두면, 사람 판단이 필요한 부분을 미리 추려낼 수 있어.

### 2) 배포 전 리스크 점검

`/codex:adversarial-review`는 특히 인증, 롤백, 동시성, 신뢰성 같은 민감한 지점에서 유용해.

### 3) 장시간 작업 위임

테스트 실패처럼 시간이 오래 걸리는 작업은 `/codex:rescue --background`로 넘겨두고, 결과는 나중에 `/codex:status`와 `/codex:result`로 확인하면 흐름이 깨지지 않는다.

## 동작 방식

이건 외부 서버를 새로 띄우는 방식이 아니라,
현재 머신에 있는 Codex CLI/App server와 동일한 인증 상태, 동일한 설정을 사용한다.

그래서 장점은 분명해.

- 기존 Codex 로그인/구성을 재사용
- 같은 레포 환경에서 바로 실행
- 결과를 다시 Codex 세션으로 이어가 확인 가능

반대로 주의점도 있어.

- 멀티파일 대규모 변경은 시간이 오래 걸릴 수 있음
- 백그라운드 실행 시 사용량이 예상보다 늘 수 있음
- review gate를 켜면 stop 훅이 반복되어 세션 비용이 증가할 수 있음

> `review gate`는 장치 동작 보장을 위해 유용하지만, 오래 켜두면 루프가 길어질 수 있어.

## 한줄짜리 운영 정리

- Codex 플러그인은 Claude Code 작업 흐름에 “정밀 리뷰”와 “작업 위임”을 붙이는 브리지다.
- `/codex:review`는 변경 코드 품질 점검용, `/codex:rescue`는 실제 문제 해결 추진용으로 나눠 쓰면 된다.
- 로컬 Codex 환경을 그대로 쓰므로 계정/설정은 별도 마이그레이션이 거의 없다.

## 자주 나오는 질문

### Q. ChatGPT 구독 없으면 못 쓰나?

아니, OpenAI API key도 가능해. 다만 사용량은 Codex 쿼터 기준으로 잡힌다는 점만 기억하면 된다.

### Q. 인증은 매번 다시 해야 하나?

로컬 Codex CLI에 로그인한 상태를 기본적으로 공유해. 처음이 아니라면 대개 바로 된다.

### Q. Codex 없이 동작하나?

아니. 이 플러그인은 Codex를 호출하는 구조라, 설치·인증이 기본 전제다.

## 핵심 체크리스트

- Node.js 18.18 이상 준비
- Codex CLI 인증 상태 확인
- 플러그인 명령어 6개는 입문 전에 한 번씩 직접 실행
- 리뷰는 기본값 `read-only` 특성을 알고 사용
- 장기 작업은 background + status/result로 관리

## 한 줄 정리

Claude Code 안에서 바로 쓰는 `openai/codex-plugin-cc`는, 리뷰 품질 향상과 반복 작업 위임을 동시에 챙기는 실용형 코딩 도우미야.

---

*이 글은 `openai/codex-plugin-cc` 공개 README 내용을 바탕으로 초보자 관점으로 정리한 요약이다.*
