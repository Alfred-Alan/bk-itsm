FROM python:3.6.12

WORKDIR /data/app/code
COPY . .
COPY supervisord.conf /data/app/conf/supervisord.conf
COPY itsm.ini /data/app/conf/itsm.ini

RUN python3.6 -m pip install -r /data/app/code/requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com \
    && mkdir -p /data/app/run \
    && mkdir -p /data/app/logs \
    && mkdir -p /data/app/conf

ENV BK_ENV=production \
    C_FORCE_ROOT=true \
    BK_LOG_DIR=/data/app/logs/ \
    BK_BROKER_URL=amqp://xxxx:xxxx@0.0.0.0:5672/prod_itsm \
    BKAPP_REDIS_HOST=0.0.0.0 \
    BKAPP_REDIS_PORT=6379 \
    BKAPP_REDIS_PASSWORD=xxxx \
    BKAPP_REDIS_MODE=single \
    BKAPP_REDIS_DB=1 \
    DB_HOST=0.0.0.0 \
    DB_PORT=3306 \
    DB_NAME=itsm \
    DB_USERNAME=xxxx \
    DB_PASSWORD=xxxx \
    APP_ID=itsm \
    APP_TOKEN=764b812b-727b-4db8-9c46-a34ad5bd9278a

ENTRYPOINT ["sh", "/data/app/code/bin/start_web.sh"]
