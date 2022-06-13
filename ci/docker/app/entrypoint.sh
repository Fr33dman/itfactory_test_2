#!/usr/bin/env sh

dockerize -wait tcp://${APP_DB_HOST}:${APP_DB_PORT}

# Миграция и синхронизация
python manage.py migrate --noinput

# Запуск команды
python manage.py runserver 0.0.0.0:8000
