FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-root --only main

COPY . .

RUN poetry build

FROM python:3.13-slim

EXPOSE 3000
ENV UID=2000
ENV GID=2000
ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONPATH=/home/python
ENV PYTHONUNBUFFERED=1

RUN groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init --shell /bin/bash -u "${UID}" -g "${GID}" python

COPY --from=builder /app/dist/*.whl /tmp

RUN pip install --no-cache-dir /tmp/*.whl \
  && rm /tmp/*.whl

USER python
WORKDIR /home/python

COPY --chown=python:python app ./app
COPY --chown=python:python db ./db

CMD ["sh", "-c", "init_db && alembic -c db/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 3000"]