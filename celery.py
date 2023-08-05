# celery.py

import os
from celery import Celery

# 기본 Django 설정 모듈을 사용합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery 객체를 생성합니다.
app = Celery('config')

# Celery 설정을 불러옵니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 이 프로젝트의 모든 앱에서 tasks.py 모듈을 자동으로 로드합니다.
app.autodiscover_tasks()

# 옵션: Celery Beat를 사용하여 주기적으로 작업을 실행하려면 아래 코드를 추가합니다.
from celery.schedules import crontab
app.conf.beat_schedule = {
    'fetch-and-save-data': {
        'task': 'map_alarm.tasks.fetch_and_save_data',
        'schedule': crontab(minute=0, hour=0),  # 매일 자정에 실행
    },
}
