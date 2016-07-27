sudo celery -A pushengine worker -f pushengine/log/celery.log -l info

sudo celery -A pushengine beat -f pushengine/log/beat.log -s pushengine/celerybeat-schedule
