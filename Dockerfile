FROM python:3.12-slim

ARG MODULE_VERSION

COPY entrypoint.sh /

RUN pip install auto-tag==$MODULE_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "/entrypoint.sh" ]
