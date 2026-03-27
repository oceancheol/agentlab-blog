---
title: "Claude Code on the Web 정리: 브라우저에서 코딩 에이전트 돌리기"
date: 2026-03-27
draft: false
image: "images/posts/claude-code-on-the-web.jpg"
tags: ["Claude Code", "Web", "Auto-fix", "GitHub", "클라우드", "개발도구"]
description: "Claude Code on the Web이 무엇인지, PR Auto-fix는 어떻게 쓰는지 초보자도 이해하기 쉽게 정리한 글이다."
---

`Claude Code on the Web`은 한마디로 말하면 **VS Code나 터미널 없이, 브라우저에서 Claude Code를 클라우드로 실행하는 기능**이야.

내 로컬 컴퓨터에 코드가 없어도 되고, 심지어 아이폰 앱에서 작업을 던져놓고 결과만 받을 수도 있어.

## 왜 필요한가

기존 Claude Code는 내 컴퓨터에서 터미널로 실행해야 했어. 그러다 보니 이런 불편함이 있었지.

- 노트북을 닫으면 작업이 멈춤
- 여러 작업을 동시에 돌리기 어려움
- 로컬에 저장소가 없는 코드는 작업 불가

Claude Code on the Web은 이 문제를 해결해줘. Anthropic 서버에서 Claude가 직접 작업하니까, 내 컴퓨터가 꺼져 있어도 계속 돌아가.

## 어떻게 동작하나

1. **claude.ai/code** 접속 후 GitHub 계정 연결
2. 저장소 선택하고 작업 내용 입력
3. Anthropic 서버에서 저장소를 클론해서 작업 시작
4. 완료되면 브랜치에 push → PR 생성

작업 중에는 웹에서 실시간으로 진행 상황을 볼 수 있고, Claude에게 추가 지시도 가능해.

## 핵심 기능: PR Auto-fix

이게 제일 실용적인 기능이야.

PR을 올린 뒤 CI가 실패하거나 리뷰어가 코멘트를 달면, **Claude가 자동으로 확인하고 수정해서 push**해줘.

### 어떻게 쓰나

- **Web에서 만든 PR**: CI 상태바에서 "Auto-fix" 버튼 선택
- **모바일 앱**: "watch this PR and fix any CI failures" 라고 말하기
- **기존 PR**: PR URL 붙여넣고 auto-fix 요청

### Claude가 판단하는 방식

- **명확한 수정**: 자신 있으면 바로 수정 후 push, 세션에 설명 남김
- **애매한 요청**: 아키텍처적으로 중요한 결정은 먼저 물어봄
- **중복/불필요**: 아무 것도 안 하고 기록만 남김

리뷰 코멘트 스레드에는 Claude가 직접 GitHub 댓글을 달기도 해. 단, 내 계정 이름으로 달리고 "Claude Code가 작성했다"는 표시가 붙어.

## 터미널 ↔ 웹 이동

### 터미널 → 웹

```bash
claude --remote "Fix the authentication bug in src/auth/login.ts"
```

이렇게 하면 웹 세션이 새로 생겨서 클라우드에서 실행돼. 나는 로컬에서 다른 작업 계속 가능.

여러 개 동시에도 됨:

```bash
claude --remote "Fix the flaky test in auth.spec.ts"
claude --remote "Update the API documentation"
claude --remote "Refactor the logger"
```

### 웹 → 터미널

웹에서 진행 중이던 작업을 로컬로 가져오려면:

```bash
claude --teleport
```

또는 Claude Code 안에서 `/teleport` 입력.

## 사용 조건

- Pro, Max, Team, Enterprise 플랜
- GitHub 저장소만 지원 (GitLab은 아직 미지원)
- Claude GitHub App 설치 필요 → [github.com/apps/claude](https://github.com/apps/claude)

## 정리

| 기능 | 내용 |
|------|------|
| 실행 위치 | Anthropic 클라우드 서버 |
| 로컬 필요 여부 | 없어도 됨 |
| PR Auto-fix | CI 실패/리뷰 코멘트 자동 수정 |
| 병렬 작업 | 여러 세션 동시 실행 가능 |
| 모바일 지원 | iOS/Android 앱에서 모니터링 |

로컬에서 Claude Code 쓰다가 "이거 그냥 백그라운드에서 돌리면 안 되나?" 싶었다면, 딱 그 용도야.
