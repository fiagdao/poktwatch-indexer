#!/bin/sh

#python manage.py migrate --no-input
cd poktwatch
echo $(ls)
python manage.py collectstatic --no-input

gunicorn poktwatch.wsgi:application --bind 0.0.0.0:8000  --log-level debug --error-logfile gunicorn_error.log
