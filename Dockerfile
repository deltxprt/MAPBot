FROM golang:1.19-alpine3.17 AS builder

RUN apk upgrade \
    && apk update

WORKDIR /mapbot

COPY . .

RUN go build ./cmd/discord \
    && mv discord mapbot-v2

FROM golang:1.19-alpine3.17

WORKDIR /mapbot

COPY --from=builder mapbot-v2 .

CMD [ "./mapbot-v2" ]