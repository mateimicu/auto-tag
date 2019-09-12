FROM python:3.7.4-alpine3.10

COPY entrypoint.sh /
COPY requirements.txt /

RUN pip install auto-tag==${MODULE_VERSION} && pip install -r /requirements.txt
RUN apk add git

ENTRYPOINT [ "/entrypoint.sh" ]
