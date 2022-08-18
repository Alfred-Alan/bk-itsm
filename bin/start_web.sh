#!/bin/bash

# 当前脚本目录
SCRIPT_DIR=$(dirname $(readlink -f "$0"))

cat << EOF
SCRIPT_DIR -> "$SCRIPT_DIR"
EOF

sh ${SCRIPT_DIR}/migrate.sh >> /data/app/logs/itsm/migrate.log \
&& python manage.py collectstatic --noinput >> /data/app/logs/itsm/collectstatic.log \
&& /usr/local/bin/supervisord -n -c /data/app/conf/supervisord.conf
