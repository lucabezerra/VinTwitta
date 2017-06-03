web: gunicorn VinTwitta.wsgi --limit-request-line 8188 --log-file -
worker: celery worker --app=VinTwitta --loglevel=info
