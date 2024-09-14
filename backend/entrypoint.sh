#!/bin/sh

python manage.py migrate --no-input
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000