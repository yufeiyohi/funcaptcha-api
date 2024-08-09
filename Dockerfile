FROM python:3.10-slim-bullseye

LABEL maintainer="yufeiyohi@outlook.com"
ARG TZ='Asia/Shanghai'

ENV BUILD_PREFIX=/app

ADD . ${BUILD_PREFIX}

RUN apt-get update \
    &&apt-get install -y --no-install-recommends bash wget vim \
    && cd ${BUILD_PREFIX} \
    && /usr/local/bin/python -m pip install --no-cache --upgrade pip \
    && pip install --no-cache -r requirements.txt \
    && chmod +x ${BUILD_PREFIX}/downloadmodel.sh \
    && bash ${BUILD_PREFIX}/downloadmodel.sh

ENV PORT=8282
EXPOSE $PORT

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD uvicorn main:app --host 0.0.0.0 --port $PORT