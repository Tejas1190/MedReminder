@echo off

REM Start Redis on port 6380
start "Redis Server" cmd /k "redis-server --port 6380"

REM Start Celery worker
start "Celery Worker" cmd /k "call MedReminder\venv\Scripts\activate && cd MedReminder && celery -A MedReminder worker --loglevel=info"

REM Start Celery beat
start "Celery Beat" cmd /k "call MedReminder\venv\Scripts\activate && cd MedReminder && celery -A MedReminder beat --loglevel=info"

REM Start Django server
start "Django Server" cmd /k "call MedReminder\venv\Scripts\activate && cd MedReminder && python manage.py runserver"
