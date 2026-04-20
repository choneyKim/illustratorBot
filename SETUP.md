# 일러스트 강사봇 셋업 가이드

> 작성일: 2026-04-12  
> 환경: Windows 11, Claude Code CLI, Claude Desktop 앱

---

## 시스템 구조 (핵심 개념)

```
[미니PC 24시간 가동]
  ├─ [역할 1] Claude Code 24/7 실행 (start_bot.bat)
  │    └─ claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions
  │         → 사용자가 Telegram에서 메시지 보내면 Claude가 수업 응답
  │
  └─ [역할 2] Claude Desktop 앱 → Schedule → illustration-daily-reminder
       └─ 매일 17:00 자동 실행 → Telegram으로 "학습시간입니다" 알림 전송
```

**⚠️ 이 두 가지는 완전히 별개다.**  
- 채널 세션이 꺼지면 → 사용자 메시지에 응답 안 됨  
- Desktop Scheduled Task가 없으면 → 17:00 알림 안 옴  
- 둘 다 있어야 완전하게 동작함

---

## 파일 구조

```
D:/illustratorBot/
├── claude.md          # Claude 행동 지침 (봇 역할/규칙 정의)
├── curriculum.md      # 17주차 커리큘럼 전체 내용
├── progress.json      # 진도 상태 (week/day/과제 상태 등)
├── .env               # Telegram 토큰/채팅ID (절대 공유 금지)
├── start_bot.bat      # 채널 세션 자동 시작 + 크래시 재시작 스크립트
└── SETUP.md           # 이 파일
```

---

## 최초 설치 순서

### 1단계. 사전 준비

- [ ] [Claude Code CLI](https://claude.ai/download) 설치 및 로그인
- [ ] [Claude Desktop 앱](https://claude.ai/download) 설치 및 로그인
- [ ] [Bun](https://bun.sh) 설치

```powershell
# Bun 설치 (PowerShell)
powershell -c "irm bun.sh/install.ps1 | iex"
```

> **⚠️ 주의: Bun 없으면 Telegram 봇이 완전히 무반응이다.**  
> "Listening for channel messages from: plugin:telegram..." 메시지가 떠도  
> Bun이 없으면 실제 봇 서버가 실행되지 않아 아무 메시지도 수신 안 됨.

### 2단계. Telegram 봇 생성

1. Telegram에서 [@BotFather](https://t.me/BotFather) 열기
2. `/newbot` 전송 → 이름 입력 → `bot`으로 끝나는 username 입력
3. 발급된 토큰 복사 (`123456789:AAH...` 형태)
4. `.env` 파일에 토큰 입력:

```
TELEGRAM_BOT_TOKEN=여기에_토큰_입력
TELEGRAM_CHAT_ID=여기에_채팅ID_입력  ← 3단계 완료 후 채움
```

### 3단계. Telegram 플러그인 설치 및 페어링

Claude Code 터미널에서:

```bash
/plugin marketplace add anthropics/claude-plugins-official
/plugin install telegram@claude-plugins-official
/reload-plugins
/telegram:configure <YOUR_BOT_TOKEN>
```

채널 활성화하여 재시작:

```bash
claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions
```

Telegram에서 봇에 아무 메시지 전송 → 페어링 코드 수신 → Claude Code에서:

```
/telegram:access pair <받은코드>
/telegram:access policy allowlist
```

> **⚠️ 주의: TELEGRAM_CHAT_ID는 페어링 후 확인해야 한다.**  
> `.env`에 넣을 TELEGRAM_CHAT_ID는 BotFather에서 주는 게 아니다.  
> 페어링 완료 후 `~/.claude/channels/telegram/access.json`의  
> `allowFrom` 배열 첫 번째 값이 실제 chat_id다.  
>
> 예시:
> ```json
> { "allowFrom": ["8777888087"] }  ← 이 값을 TELEGRAM_CHAT_ID에 입력
> ```

### 4단계. .env 최종 업데이트

```
TELEGRAM_BOT_TOKEN=8258836223:AAF_Khr...  (BotFather 발급 토큰)
TELEGRAM_CHAT_ID=8777888087               (access.json allowFrom 값)
```

### 5단계. Desktop Scheduled Task 등록 (매일 17:00 알림)

Claude Desktop 앱 → 사이드바 **Schedule** → **New task** → **New local task**

| 항목 | 값 |
|------|-----|
| Name | `illustration-daily-reminder` |
| Frequency | Daily, 17:00 |
| Project folder | `D:\illustratorBot` |
| Permission mode | Auto |

**Prompt:**
```
D:/illustratorBot/progress.json을 읽어서 현재 week(W)와 day(D)를 확인하라.

다음 수업 계산:
- D < 7이면 → 다음 수업 = W주 (D+1)일차
- D = 7이면 → 다음 수업 = (W+1)주 1일차

강의자료 사전 생성 (핵심):
1. lessons/week{W:02d}_day{D+1}.html 파일이 있는지 확인
2. 없으면:
   - D:/illustratorBot/curriculum.md에서 해당 일차 스펙 읽기
   - 스펙의 이미지 키워드로 WebSearch → 실제 이미지 URL 2~3개 확보
   - CLAUDE.md의 HTML 강의자료 생성 규칙에 따라 HTML 생성
   - lessons/week{W:02d}_day{D+1}.html 로 저장
3. 있으면 → 건너뜀

알림 전송:
D:/illustratorBot/.env에서 TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 읽어라.
D:/illustratorBot/curriculum.md에서 해당 일차의 오늘의 목표 첫 줄을 읽어라.
아래 형식으로 curl로 Telegram 메시지를 전송하라:

"📚 일러스트 학습시간입니다!

오늘: [W]주 [D+1]일차 — [오늘의 목표 첫 줄]

클로드에게 '시작' 이라고 보내면 수업을 시작합니다."
```

저장 후 **Run now**로 테스트.

> **⚠️ 주의: 처음 실행 시 권한 허용 팝업이 뜬다.**  
> Node.js 또는 curl 실행 권한을 요청함. **"항상 허용(Always allow)"** 선택해야  
> 다음부터 자동으로 실행됨. 그냥 허용만 하면 매번 물어봄.

### 6단계. 미니PC 자동 시작 등록

PowerShell **관리자 권한**으로 실행:

```powershell
$action = New-ScheduledTaskAction `
  -Execute "cmd.exe" `
  -Argument "/c D:\illustratorBot\start_bot.bat" `
  -WorkingDirectory "D:\illustratorBot"

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
  -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
  -RestartCount 5 `
  -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
  -TaskName "IllustratorBot" `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -RunLevel Highest `
  -Force
```

지금 즉시 시작:
```powershell
Start-ScheduledTask -TaskName "IllustratorBot"
```

---

## 미니PC 이전 시 체크리스트

- [ ] Claude Code CLI 설치 (`winget install Anthropic.Claude` 또는 공식 사이트)
- [ ] Claude Desktop 앱 설치
- [ ] Bun 설치 (`powershell -c "irm bun.sh/install.ps1 | iex"`)
- [ ] 이 프로젝트 폴더 통째로 복사 (`D:\illustratorBot`)
- [ ] Claude Code에서 claude.ai 계정 로그인
- [ ] 3단계부터 다시 진행 (플러그인 설치 → 페어링 → Desktop Task 등록 → Task Scheduler 등록)
- [ ] `.env`의 TELEGRAM_CHAT_ID 재확인 (새 페어링 후 바뀔 수 있음)

---

## 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| 봇에 메시지 보내도 무반응 | `start_bot.bat` 안 켜져 있음 | PowerShell에서 `claude --channels...` 실행 또는 Task Scheduler 확인 |
| 봇에 메시지 보내도 무반응 (2) | Bun 미설치 | `bun --version` 확인 후 설치 |
| 17:00 알림 안 옴 | Desktop Scheduled Task 꺼져있거나 Desktop 앱 종료됨 | Claude Desktop 앱 켜고 Schedule 확인 |
| "chat not found" 오류 | TELEGRAM_CHAT_ID 틀림 | `access.json`의 `allowFrom` 값으로 수정 |
| Desktop Task 권한 팝업 계속 뜸 | 허용 시 "항상 허용" 안 누름 | Task 상세 → Always allowed 패널 확인 |
| 페어링 코드 안 옴 | Bun 미설치 또는 채널 세션 미실행 | Bun 설치 확인, `--channels` 플래그로 재시작 |
