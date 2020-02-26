#!/usr/bin/env bash

python manage.py migrate
#echo "from django.contrib.auth.models import User; try: User.objects.create_superuser('admin', '', 'pass') except: pass" | python manage.py shell
python manage.py runserver 0.0.0.0:8000