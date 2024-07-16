FROM python:3.12.4

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim

RUN pip install --upgrade pip

COPY pkg/ /app/

RUN pip install .

ENTRYPOINT ["networth"]
