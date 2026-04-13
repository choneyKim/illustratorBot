@echo off
title 일러스트 강사봇 - Claude Channels
cd /d D:\illustratorBot

:loop
echo [%date% %time%] Claude Code 시작 중...
claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions
echo [%date% %time%] 종료됨. 10초 후 재시작...
timeout /t 10 /nobreak
goto loop
