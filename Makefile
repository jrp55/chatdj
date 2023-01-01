.PHONY: image
CONTAINER_ENGINE ?= docker

image:
	${CONTAINER_ENGINE} build -t chatdj:0.0.1 .
