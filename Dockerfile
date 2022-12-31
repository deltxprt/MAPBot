FROM golang:1.19-alpine3.17 AS builder

RUN apk upgrade \
    && apk update

FROM golang:1.19-alpine3.17

WORKDIR /mapbot

COPY . .

RUN go build ./cmd/discord

CMD [ "./mapbot-v2" ]