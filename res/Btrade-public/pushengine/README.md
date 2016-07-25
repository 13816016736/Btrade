celery -A pushengine worker -f pushengine/log/celery.log -l info

celery -A pushengine beat -s pushengine/celerybeat-schedule