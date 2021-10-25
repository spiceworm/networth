FROM python:3.9.6

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim

RUN pip install --upgrade pip

COPY pkg/ /app/

RUN pip install . --use-feature=in-tree-build

ENTRYPOINT ["networth"]
