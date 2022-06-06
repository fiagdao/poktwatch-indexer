ARG GOLANG_IMAGE_VERSION=golang:1.16.2-alpine3.13
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

RUN git clone --branch staging https://github.com/dragondmoney/pocket-core.git ${POCKET_PATH}
RUN cd ${POCKET_PATH}
RUN go build -tags cleveldb -o ${GOBIN}/bin/pocket ./app/cmd/pocket_core/main.go

FROM alpine:3.15 AS pocket

COPY --from=builder /bin/pocket /bin/pocket

RUN apk add --update --no-cache expect bash leveldb-dev

ENV PYTHONUNBUFFERED=1

RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

RUN apk add python3-dev libpq-dev gcc musl-dev

RUN addgroup --gid 1001 -S app
RUN adduser --uid 1005 -S -G app app
RUN chown -R app /bin/pocket  && mkdir -p /home/app/.pocket/config

RUN chown -R app /home/app/.pocket

RUN pip install --upgrade pip

RUN apk add libffi-dev

RUN apk add git

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN git clone https://github.com/pokt-foundation/pypocket
RUN pip install wheel
RUN pip install -e ./pypocket

COPY ./ /backend

WORKDIR /backend

COPY ./entrypoint.sh /

ENTRYPOINT ["sh", "/entrypoint.sh"]
