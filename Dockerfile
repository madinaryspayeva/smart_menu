FROM python:3.13-slim-bullseye
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

COPY . .

CMD sh -c "poetry run python manage.py migrate --noinput && poetry run gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2 --worker-class gthread --access-logfile - --error-logfile - --log-level info"