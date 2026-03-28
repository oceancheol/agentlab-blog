---
title: "Claude Code 하네스란? 스타 10만 개 넘은 everything-claude-code 정리"
date: 2026-03-28
draft: false
image: "images/posts/claude-code-harness.jpg"
tags: ["Claude Code", "하네스", "에이전트", "everything-claude-code", "개발도구", "오픈소스"]
description: "Claude Code 하네스가 뭔지, 스타 10만 개를 넘긴 everything-claude-code는 어떻게 쓰는지 초보자도 이해하기 쉽게 정리한 글이다."
---

Claude Code를 쓰다 보면 "하네스(harness)"라는 말이 종종 나와. 근데 이게 뭔지 선뜻 와닿지 않는 경우가 많아. 오늘은 하네스 개념부터 시작해서, 현재 GitHub 스타 10만 개를 넘긴 `everything-claude-code`까지 정리해볼게.

## 하네스가 뭔가

하네스는 원래 마구(馬具), 즉 말을 제어하는 장비를 뜻해. Claude Code에서 하네스는 **AI가 더 잘 작동하도록 감싸는 설정과 구조의 집합**이야.

한마디로 말하면 이거야:

> Claude Code 자체는 엔진이고, 하네스는 그 엔진을 더 잘 쓸 수 있게 만드는 주변 장치 전체야.

구체적으로는 이런 것들이 들어가:

- **Skills**: Claude가 특정 작업을 할 때 따르는 워크플로우 정의
- **Rules**: 항상 지켜야 할 코딩 스타일, 테스트 기준 같은 규칙
- **Hooks**: 특정 이벤트(파일 저장, 세션 시작 등)에 자동 실행되는 명령
- **Agents**: 특정 역할을 맡는 전문 서브에이전트
- **Commands**: `/plan`, `/review` 같은 즉시 실행 명령어

## everything-claude-code

2025년 9월 Anthropic 해커톤에서 우승한 프로젝트야. 만든 사람은 Affaan Mustafa로, 10개월 넘게 실제 제품 개발에 쓰면서 만들어온 설정 시스템이야.

처음에는 개인 설정 파일로 시작했는데, 오픈소스로 공개하자마자 폭발적으로 퍼져서 지금은 **GitHub 스타 10만 개**를 넘겼어.

### 뭐가 들어있나

| 구성 요소 | 수량 | 설명 |
|----------|------|------|
| Agents | 28개 | 코드 리뷰, 보안 검토, 언어별 빌드 오류 해결 등 |
| Skills | 70개+ | 프레임워크별 패턴, TDD, 기사 작성, 시장 조사 등 |
| Commands | 30개+ | `/plan`, `/tdd`, `/code-review`, `/e2e` 등 |
| Rules | 언어별 | TypeScript, Python, Go, Java, Rust, Swift 등 10개 언어 |

### 특징

**크로스플랫폼**: Claude Code뿐 아니라 Cursor, OpenCode, Codex에서도 돌아가.

**지속 학습**: 세션에서 발견한 패턴을 자동으로 추출해서 Instinct → Skill로 진화시켜. 쓸수록 똑똑해지는 구조야.

**보안**: AgentShield 통합, CVE 스캔, 샌드박싱 기능 포함.

**멀티에이전트 오케스트레이션**: PM2 기반으로 복잡한 워크플로우를 여러 에이전트가 나눠서 처리.

### 설치 방법

```bash
# 방법 1: 플러그인으로 설치
/plugin marketplace add affaan-m/everything-claude-code

# 방법 2: 수동 설치
git clone https://github.com/affaan-m/everything-claude-code.git
./install.sh typescript  # python, golang, swift 등 선택 가능
```

Rules는 플러그인으로 배포가 안 돼서 수동 설치가 필요해.

## 주목할 만한 다른 하네스 프로젝트

### awesome-claude-code-toolkit

에이전트 135개, 큐레이션된 스킬 35개(SkillKit으로 40만 개+), 명령어 42개, 플러그인 150개+ 등을 모아놓은 종합 툴킷.

👉 [github.com/rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)

### Citadel

4단계 라우팅, 세션 간 캠페인 지속성, 독립된 워크트리에서 병렬 에이전트 실행, 서킷 브레이커 등 기업 규모 운영에 특화된 오케스트레이션 하네스.

👉 [github.com/SethGammon/Citadel](https://github.com/SethGammon/Citadel)

### your-claude-engineer

Slack, GitHub, Linear에 연결해서 실제 소프트웨어 엔지니어처럼 작동하는 에이전트 하네스 데모.

👉 [github.com/coleam00/your-claude-engineer](https://github.com/coleam00/your-claude-engineer)

## 정리

하네스는 Claude Code를 더 잘 쓰기 위한 설정과 구조의 집합이야. 맨 바닥에서 시작하면 매번 같은 걸 설명해야 하지만, 하네스가 있으면 Claude가 처음부터 맥락을 알고 시작해.

everything-claude-code는 그중에서 가장 많이 쓰이는 하네스야. 스타 10만 개는 그냥 쌓인 게 아니라, 실제로 쓰는 개발자가 그만큼 많다는 뜻이야.
