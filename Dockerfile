FROM python:3.11.0b1-slim-bullseye

ADD bot /

RUN python -m pip install --upgrade pip

RUN pip install discord requests

CMD [ "python", "./MAPBot.py" ]
