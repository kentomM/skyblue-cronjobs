FROM python:3.10 AS builder

ADD pyproject.toml .
ADD poetry.lock .

RUN pip install poetry \
 && poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder requirements.txt .
RUN pip install -r requirements.txt

COPY scripts .
