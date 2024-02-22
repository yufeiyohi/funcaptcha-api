FROM python:3.10
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
#RUN apk add --no-cache musl-dev openssl-dev libffi-dev tzdata gcc ttf-dejavu
#RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

COPY . /app/
WORKDIR /app
#RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT=8181
EXPOSE $PORT

CMD uvicorn main:app --host 0.0.0.0 --port $PORT