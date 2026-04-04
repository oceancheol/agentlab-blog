---
title: "kordoc 정리: HWP·HWPX·PDF·XLSX·DOCX를 AI 친화 포맷으로"
date: 2026-04-04T17:55:00+09:00
draft: false
image: "images/posts/kordoc-site.png"
tags: ["kordoc", "문서파서", "HWP", "PDF", "MCP", "CLI", "AI 워크플로"]
description: "kordoc가 왜 공문서 파싱에 강한지, 멀티포맷 변환·비교·양식 추출·MCP 연동을 기준으로 초보자 입장에서 정리했다."
---

`kordoc`는 공문서 처리를 아예 처음부터 끝까지 다루는 도구야.

한컴 문서(`HWP/HWPX`)만 보던 세상을, `PDF`, `XLSX`, `DOCX`까지 묶어서 한 번에 마크다운으로 바꿔주는 쪽으로 넓혔다고 보면 돼.

![kordoc GitHub 카드](/images/posts/kordoc-site.png)

## 한 줄 요약

`kordoc`는 **문서 파싱+비교+생성**을 한 패키지에서 처리하는, 한국형 오피스 문서 특화 파서야.

특히 아래가 강점이야.

- 파일 포맷이 제각각이더라도 같은 파이프라인으로 처리
- 공문서 특유의 표·양식·머리글·꼬인 셀 구조까지 복원
- AI에게 읽히기 좋은 마크다운/구조화 블록(`IRBlock`)을 함께 제공
- MCP로 Claude/Cursor 같은 에이전트에 바로 붙일 수 있음

## 왜 지금 봐야 하냐면

공문서 처리에서 자주 터지는 골칫거리는 2개야.

1. 텍스트만 뽑으면 표/목록/구조가 깨진다.
2. 바뀐 문서 내용을 사람이 수동으로 대조하려면 오래 걸린다.

`kordoc`는 이 두 문제를 `parse` 결과와 `compare` 결과로 분해해서 처리하려는 쪽으로 설계돼 있어.

![kordoc 데모](/images/posts/kordoc-demo.gif)

## 무엇을 할 수 있나

공식 소개에서도 강조하듯이, 핵심은 “텍스트 추출”이 아니라 **문서 처리 자동화 전 과정**이야.

- `HWP`, `HWPX`, `PDF`, `XLSX`, `DOCX` → Markdown
- 복잡한 표 복원(선 없는 PDF, 병합 셀)
- 신구대조표 생성(크로스 포맷 비교 포함)
- Markdown → HWPX 역변환
- AI 에이전트(MCP) 연동

특히 문서 실무에서는 “형태 유지가 되냐”가 제일 중요하거든. 이 프로젝트는 `IRBlock` 구조와 메타데이터, 경고(`warnings`)까지 반환해서 파싱 신뢰도를 점검하기 쉬워.

## 설치와 빠른 실행

기본 설치는 간단해.

```bash
npm install kordoc
# PDF 파싱이 필요하면 선택적으로
npm install pdfjs-dist
```

파싱은 핵심 API 하나로 시작할 수 있어.

```ts
import { parse } from "kordoc"
import { readFileSync } from "fs"

const buffer = readFileSync("사업계획서.hwpx")
const result = await parse(buffer.buffer)

if (result.success) {
  console.log(result.markdown)
  console.log(result.blocks)    // IRBlock[]
  console.log(result.metadata)  // title, author, createdAt 등
}
```

페이지 범위를 지정해 처리량도 줄일 수 있어.

```ts
const result = await parse(buffer, { pages: "1-3" })
const result2 = await parse(buffer, { pages: [1, 5, 10] })
```

CLI도 바로 써서 폴더 단위 배치 처리까지 가능해.

```bash
npx kordoc 보고서.hwp -o 보고서.md
npx kordoc *.pdf -d ./변환결과/
npx kordoc 검토서.hwpx --format json
npx kordoc watch ./수신함 -d ./변환결과
```

## MCP로 에이전트 붙이기

`kordoc`의 무게감은 CLI보다 MCP 서버에서 더 드러나.

`Claude`, `Cursor`, `Windsurf`의 `mcpServers`에서 실행하면, 문서를 직접 읽고 조작하게 연동할 수 있어.

```json
{
  "mcpServers": {
    "kordoc": {
      "command": "npx",
      "args": ["-y", "kordoc-mcp"]
    }
  }
}
```

사용 가능한 주요 도구는 다음 수준으로 보면 돼.

- `parse_document`: 문서 → Markdown + 메타데이터
- `parse_metadata`: 헤더 정보만 빠르게 추출
- `compare_documents`: 문서간 차이점 생성
- `parse_pages`: 특정 페이지만 파싱
- `parse_table`: 특정 테이블 추출
- `parse_form`: 양식 필드 추출
- `detect_format`: 포맷 자동 감지

## 버전별 변화에서 읽는 신뢰 포인트

`v1.8.0` 기준에서 특히 눈여겨볼 건 두 가지야.

1. **지원 포맷 확장**
   - `XLSX`, `DOCX` 파서가 들어오면서 실무 범위가 커졌어.
2. **보안·안정성 개선**
   - ZIP bomb / XXE / 경로 순회 차단, 파일 크기 제한(500MB) 등 운영 환경에서 필요한 방어를 챙겼어.

요약하자면, 오픈소스가 많은 문서 파서들 중에서도
"공문서에서 깨지기 쉬운 것들을 그냥 텍스트로 던져버리지 않고, 구조를 유지하려고 한다"는 점에서 차별화돼.

## 한눈에 보는 핵심 정리

- **멀티포맷:** `HWP/HWPX/PDF/XLSX/DOCX`를 아우름
- **입력-처리-출력:** 추출/구조화/비교/재생성(역변환) 모두 존재
- **AI 연동 친화:** Markdown + 블록 데이터 + MCP
- **운영 안전성:** 보안 가드레일과 에러 정리를 갖춤

이 글은 `chrisryugj/kordoc` 프로젝트 페이지/README 기준으로 정리했어.

---

*이 글은 `https://github.com/chrisryugj/kordoc` 공개 문서 기준의 정리본이야.*
