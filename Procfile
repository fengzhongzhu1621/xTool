web: gunicorn apps.wsgi -w 4 -b :$PORT --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s "%(r)s" %(s)s %(D)s %(b)s "%(f)s" "%(a)s"'
worker: python manage.py celery worker -c 4 -l info -Q er_execute,er_schedule,default,celery
