import subprocess
import sys

from celery import Celery

app = Celery('biohacking', broker='pyamqp://guest@10.8.16.18//')

app.autodiscover_tasks(['core.utils.tasks'])

def start_celery_worker():
    # Запуск Celery worker как subprocess
    return subprocess.Popen([
        sys.executable, '-m', 'celery',
        '-A', 'core.utils.celery_app',
        'worker',
        '--loglevel=info',
        '--pool=threads',
        '--hostname=worker1@%h'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
