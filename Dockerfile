FROM golang:1.19-alpine3.17

RUN apk upgrade \
    && apk update

WORKDIR /mapbot

COPY . .

RUN go build ./cmd/discord

CMD [ "./mapbot-v2" ]