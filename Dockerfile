FROM python:3.10-alpine3.14 as builder

WORKDIR /mapbot

COPY bot /mapbot/bot

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk upgrade \
    python -V

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /mapbot/wheels -r requirements.txt


FROM python:3.10-alpine3.14

WORKDIR /mapbot

COPY --from=builder /mapbot/bot .
COPY --from=builder /mapbot/wheels /wheels
COPY --from=builder /mapbot/requirements.txt .

RUN pip install --no-cache /wheels/*

CMD [ "python", "./MAPBot.py" ]