FROM golang:1.19-alpine3.17

RUN apk upgrade \
    && apk update

WORKDIR /building

COPY . .

RUN go build ./cmd/discord

WORKDIR /mapbot

RUN mv /building/discord /mapbotv2

CMD [ "/mapbotv2" ]