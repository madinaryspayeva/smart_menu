FROM python:3.13-slim-bullseye
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir /code

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .
