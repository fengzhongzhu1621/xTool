#!/bin/bash
# python manage.py makemigrations
# python manage.py migrate --no-input
# python manage.py createcachetable
# python manage.py init -y
uvicorn apps.asgi:application --port 8000 --host 0.0.0.0 --workers 4
