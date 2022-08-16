FROM python:3.11-rc-slim

ARG MODULE_VERSION

COPY entrypoint.sh /

RUN pip install auto-tag==$MODULE_VERSION
RUN apk add git

ENTRYPOINT [ "/entrypoint.sh" ]
