#!/bin/sh

python manage.py migrate --no-input
python manage.py initadmin

gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000