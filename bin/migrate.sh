#!/bin/bash

# 构建数据库表
python manage.py migrate --no-input \
&& python manage.py createcachetable django_cache
