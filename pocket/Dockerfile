ARG GOLANG_IMAGE_VERSION=golang:1.17.2-alpine3.13
FROM ${GOLANG_IMAGE_VERSION} AS builder

RUN apk -v --update --no-cache add \
	curl \
	git \
	groff \
	less \
	mailcap \
	gcc \
	libc-dev \
	bash  \
	leveldb-dev && \
	rm /var/cache/apk/* || true

ENV POCKET_PATH=/go/src/github.com/pokt-network/pocket-core/
ENV GO111MODULE="on"

RUN mkdir -p ${POCKET_PATH}

WORKDIR $POCKET_PATH

RUN git clone --branch RC-0.9 https://github.com/dragondmoney/pocket-core.git ${POCKET_PATH}
RUN cd ${POCKET_PATH}
RUN go build -tags cleveldb -o ${GOBIN}/bin/pocket ./app/cmd/pocket_core/main.go

FROM alpine:3.13

COPY --from=builder /bin/pocket /bin/pocket

RUN apk add --update --no-cache expect bash leveldb-dev

RUN mkdir -p ~/.pocket/config

COPY config.json ~/.pocket/config/config.json

USER root
WORKDIR /home/app
COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
