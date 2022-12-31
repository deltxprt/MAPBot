FROM golang:1.19-alpine3.17

WORKDIR /mapbot

COPY ./mapbot-v2 .

RUN apk upgrade \
    apk update

CMD [ "./mapbot-v2" ]