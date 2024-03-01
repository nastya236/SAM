#!/bin/bash
# Build, test and push experiment container.

set -xe


if [[ -z $(git status --porcelain) ]]; then
  TAG=$(git rev-parse --short HEAD)
else
  TAG=dev
fi

BASENAME=sam/dev
DOCKERNAME=$BASENAME:$TAG
LATEST=$BASENAME:latest
echo Building $DOCKERNAME

docker build \
	--build-arg UID=$(id -u) \
	--build-arg GID=$(id -g) \
	--build-arg GIT_HASH=$(git rev-parse HEAD) \
       	-t $DOCKERNAME ../
docker tag $DOCKERNAME $LATEST

docker run \
	--gpus 1 \
	-e MYSQL_ROOT_PASSWORD=simple \
    -e DJ_HOST=db \
    -e DJ_USER=root \
    -e DJ_PWD=simple \
    -e DJ_SUPPORT_FILEPATH_MANAGEMENT=TRUE \
    -e DJ_SUPPORT_ADAPTED_TYPES=TRUE \
	-v /home/anastasia/SAM:/workspace/SAM \
	-it $DOCKERNAME
