FROM python:3.11-bookworm

RUN pip install poetry

RUN apt install -q libmariadb3 libmariadb-dev

COPY . /app

WORKDIR /app

RUN poetry install

WORKDIR /app/src

ENTRYPOINT ["poetry", "run", "python", "-m", "compass_app"]
