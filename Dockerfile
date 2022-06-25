FROM python:3.11.0b1-slim-bullseye

ADD bot /

RUN pip install discord requests==2.27.1

CMD [ "python", "./MAPBot.py" ]
