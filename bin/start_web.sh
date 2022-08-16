#!/bin/bash

python manage.py migrate --no-input >> /data/app/logs/itsm/migrate.log \
&& python manage.py createcachetable django_cache >> /data/app/logs/itsm/migrate.log \
&& /usr/local/bin/supervisord -n -c /data/app/conf/supervisord.conf
