FROM python:3.11.0b1-slim-bullseye

ADD bot /

RUN pip install discord requests

CMD [ "python", "./MAPBot.py" ]
