FROM python:3.10-alpine

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update
RUN apk add python3-dev  \
    libpq-dev  \
    libc-dev \
    musl-dev \
    libffi-dev \
    gcc
RUN pip install --upgrade pip wheel \
    && pip install psycopg2-binary

COPY app/build/pip/requirements.txt /var/app/build/pip/requirements.txt
RUN pip install -r /var/app/build/pip/requirements.txt

EXPOSE 8000
WORKDIR /var/app/

COPY ci/docker/app/entrypoint.sh /

CMD ["/entrypoint.sh"]
