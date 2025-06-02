@echo off
call venv\Scripts\activate
python manage.py runserver_plus --cert-file=localhost.pem --key-file=localhost-key.pem
pause

