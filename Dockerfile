FROM python:latest

ADD bot /

RUN pip install discord requests==2.27.1

CMD [ "python", "./MAPBot.py" ]
