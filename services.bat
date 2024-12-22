@echo off


:: Start Django server in a new window
start cmd /K "daphne -b 127.0.0.1 -p 8001 pos.asgi:application"

start cmd /K "python manage.py runserver"

:: Start Celery worker in a new window
::start cmd /K "celery -A pos worker --pool=solo -l info"

:: Start Celery Beat in a new window
::start cmd /K "celery -A pos beat --loglevel=info"


::redistart cmd /K "s-server"

echo All services are now running.
pause
