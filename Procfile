web: gunicorn kids-guardian.wsgi:map_alarm --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate