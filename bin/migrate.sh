#!/bin/bash

# 删除遗留数据库，并新建一个空的本地数据库
CREATE_DB_SQL="
create database if not exists ${DB_NAME} default character set utf8 collate utf8_general_ci;
"

if [ "$DB_PASSWORD" ]; then
  mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USERNAME" -p"$DB_PASSWORD" -sNe "$CREATE_DB_SQL"
else
  # 没有密码时无需-p，防止回车阻塞
  mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USERNAME" -sNe "$CREATE_DB_SQL"
fi

# 构建数据库表
python manage.py migrate --no-input 
python manage.py createcachetable --no-input 
