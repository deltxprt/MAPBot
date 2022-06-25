FROM python:latest

ADD bot /

RUN python -V

RUN python -m pip install --upgrade pip

RUN pip install discord requests

CMD [ "python", "./MAPBot.py" ]
