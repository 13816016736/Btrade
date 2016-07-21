celery -A pushengine worker  -l info

celery -A pushengine beat -s pushengine\celerybeat-schedule