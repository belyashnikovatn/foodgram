#!/bin/sh
python manage.py makemigrations && python manage.py migrate --noinput && python manage.py initadmin && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000