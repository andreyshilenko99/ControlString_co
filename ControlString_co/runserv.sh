#!/bin/sh
echo "Doing my thing! makemigrations, migrate, runserver..."
ls
#python manage.py flush --no-input
sleep 10
python manage.py makemigrations
sleep 2
python manage.py makemigrations
sleep 2
python manage.py migrate
sleep 2
#python manage.py runserver 0.0.0.0:8000

exec "$@"