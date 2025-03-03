FROM python:3.13.2-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim

COPY ./app/requirements.txt /tmp/

RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY ./app /app

ENTRYPOINT ["python", "/app/main.py"]
