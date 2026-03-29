---
title: "Claude iMessage 플러그인 정리: 로컬 DB 기반으로 메시지를 AI가 읽고 답하기"
date: 2026-03-29
draft: false
image: "images/posts/claude-imessage-plugin.jpg"
tags: ["Claude Code", "iMessage", "MCP", "macOS", "자동화"]
description: "Anthropic 공식 외부 플러그인 iMessage의 동작 방식, 보안 포인트, 설치/사용 흐름을 초보자 기준으로 정리했다."
---

`iMessage` 플러그인은 **Claude Code가 iMessage를 직접 읽고 답장할 수 있게 해주는 로컬 플러그인**이야.

한마디로, `~/Library/Messages/chat.db`를 읽어서 받은/보낸 문자 맥락을 가져오고, 필요하면 AppleScript로 실제 Messages 앱에 답장을 보내는 구조야.

요점은 외부 서버가 별도로 상시 동작하지 않고, 내 머신의 메시지 데이터베이스를 직접 쓰는 방식이라는 점이야.

![iMessage 플러그인 핵심 구조](/images/posts/claude-imessage-flow.jpg)

## 이 플러그인은 무엇을 해주는가

공식 설명 한 줄로 정리하면 이래.

- `chat.db`에서 메시지 히스토리를 조회해서 읽기
- 새 메시지를 초단위로 감지
- 허용한 상대만 AI에 전달
- `reply` 도구로 다시 Messages 앱에 전송

즉, Claude에게 문자 채팅처럼 동작하게 만드는 브릿지야.

## 빠른 설치 흐름

실행 순서는 단순해.

1. **권한 준비**
   - macOS의 Full Disk Access 권한을 허용해야 함
   - 처음 접근할 때 터미널(또는 IDE)에서 `chat.db` 접근 권한 질문이 떠
2. 플러그인 설치
   ```
   /plugin install imessage@claude-plugins-official
   ```
3. 새 채널로 재실행
   ```
   claude --channels plugin:imessage@claude-plugins-official
   ```
4. 텍스트 동작 확인
   - `/imessage:configure` 탭 완성 여부 확인
   - 본인 번호로 메시지 보내며 동작 확인

## 왜 self-chat은 바로 되고, 남은 사람은 allowlist가 필요한가

초기 설정 기본이 보안 중심이라, 본인 메시지는 바로 읽고 응답 가능한 반면, 다른 발신자는 별도 허용을 해야 들어와.

허용은 다음처럼 하면 돼.

```text
/imessage:access allow +15551234567
```

핸들 형태는 `+1555...` 또는 `@icloud.com` 형식이야.

`allowlist` 중심이라, 갑작스러운 수신 메시지 침입을 막는 데 유리해. 초보자 입장에서 가장 마음 편한 포인트야.

## 동작 방식을 딱 잡아보면

플러그인이 실제로 하는 일은 아래 4단계야.

- **Inbound**
  - 1초 주기로 `chat.db`를 확인해서 새 메시지를 감지
  - 물리적으로는 row ID watermark 방식으로 중복 방지
- **Outbound**
  - AppleScript(`osascript`)로 Messages 앱에 전송
- **History & Search**
  - 로컬 SQLite에서 과거 메시지 전체를 조회 가능
- **Attachments**
  - 이미지 경로를 로컬 경로로 넘겨 받아서 읽기/처리 가능

여기서 중요한 건 “부분 API”가 아니라 **로컬 DB 중심 처리**라는 점이야.

## 실무에서 장점이 보이는 지점

- 별도 클라우드 서버 의존이 적음
- macOS 생태계 메시지 작업을 AI로 연결하기 쉬움
- 과거 기록 조회까지 가능해서 맥락 유지가 좋음
- 그룹/DM 제어가 가능해서 실무 접근성이 높음

## 같이 알아둘 설정 포인트

- 자동 전송 시 첫 outbound에서 Automation 권한 팝업이 뜰 수 있어
- 권한이 안 풀리면 플러그인이 바로 종료되는 경우가 생김
- `IMESSAGE_STATE_DIR`을 바꿔서 상태 파일 위치를 운영 정책에 맞게 둘 수 있음
- `IMESSAGE_APPEND_SIGNATURE` 기본값 `true`라, 전송 본문 끝에 `Sent by Claude`가 붙을 수 있음
- `IMESSAGE_ACCESS_MODE=static`으로 두면 실행 중 동적 페어링 없이 `access.json`만 사용

## 보안 관점 한마디

이 플러그인은 메시지 데이터에 직접 접근하니까 권한이 핵심이야.

특히 내가 강조하고 싶은 건 두 가지야.

1. **권한 통제**: 기본 allowlist로 외부 유입을 막을 수 있음
2. **로컬 우선**: 외부 백엔드에 모든 기록을 올리지 않는 방향이라 데이터 이동 범위를 줄임

다만 메시지 송수신 자체는 운영 환경에서 사고 범위를 만들 수 있어. 실서비스처럼 쓰기 전에 **허용 목록**을 먼저 좁게 운영하는 게 맞아.

## 한계도 솔직히 말하면 있다

AppleScript 제약이 있어서 이런 건 못해.

- 탭백/리액션(tapback)
- 메시지 수정
- 스레드 내부 일부 고급 제어

완벽한 iMessage API 대체라기보다, **기본 텍스트 수발신 자동화**를 위한 실용적 레이어로 보는 게 맞아.

대안이 필요하면 BlueBubbles 같은 별도 방식이 있으나, SIP 해제 등 제약이 더 커진다는 점을 같이 봐야 해.

## 한 줄 요약

`iMessage` 플러그인은 Claude Code가 macOS 메시지 DB를 직접 읽고 AppleScript로 답장을 보내게 해주는 로컬 중심의 효율적인 자동화 브릿지야.

## 핵심 정리

- 설치는 간단하지만 권한/플러그인 채널 설정이 가장 중요
- 기본은 allowlist 방식으로 다른 사람 메시지를 차단
- 1초 단위 폴링으로 신규 메시지 감지
- 과거 히스토리 조회와 검색이 로컬 DB로 가능
- AppleScript 한계가 있어 완전한 메시지 제어는 아님

---

*이 글은 Anthropic 공식 iMessage 플러그인 README 내용을 바탕으로 초보자용으로 정리한 글이다.*