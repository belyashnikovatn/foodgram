#!/bin/sh
python manage.py makemigrations && python manage.py migrate --noinput && cp -r /app/media/. /media/ && python manage.py initadmin && python manage.py loadcatalogs && python manage.py loaddata recipes.json && python manage.py collectstatic --no-input --clear && cp -r /app/collected_static/. /backend_static/static/ && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000