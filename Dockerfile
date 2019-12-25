FROM python:3.7.4-alpine3.10

ARG MODULE_VERSION

COPY entrypoint.sh /

RUN pip install auto-tag==$MODULE_VERSION
RUN apk add git

ENTRYPOINT [ "/entrypoint.sh" ]
