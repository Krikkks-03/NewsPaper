@echo off
cd /d "C:\Users\Admin\PycharmProjects\NewsPortal"
call venv\Scripts\activate
python manage.py weekly_digest
pause