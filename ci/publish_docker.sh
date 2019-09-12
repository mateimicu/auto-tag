#!/usr/bin/env bash
set -x 

VERSION="$(cat setup.py | grep "version=" | cut -d= -f2 | tr -d "'" | tr -d ',')"
IMG_NAME="matei10/auto-tag:$VERSION"
docker build -t "$IMG_NAME" .
docker push "$IMG_NAME"
