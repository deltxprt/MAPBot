FROM golang:1.19-alpine3.17 AS builder

WORKDIR /mapbot

COPY ./mapbotv2 .

RUN apk upgrade \
    apk update

FROM golang:1.19-alpine3.17

WORKDIR /mapbot

COPY --from=builder /mapbot/mapbotv2 .

CMD [ "./mapbotv2" ]