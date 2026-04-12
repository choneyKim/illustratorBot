import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 매일 오후 5시 알림 (한국 표준시)
NOTIFICATION_HOUR = 17
NOTIFICATION_MINUTE = 0
TIMEZONE = "Asia/Seoul"

# 학습 시간 설정
WEEKDAY_HOURS = 3
WEEKEND_HOURS = 4

# 과제 최대 재시도 횟수 (이후 자동 진행)
MAX_RETRY_COUNT = 3
