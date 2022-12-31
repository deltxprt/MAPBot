FROM golang:1.19-alpine3.17

WORKDIR /mapbot

COPY ./mapbotv2 .

RUN apk upgrade \
    apk update

CMD [ "./mapbotv2" ]