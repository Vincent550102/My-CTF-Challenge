FROM python:3.10
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - 
WORKDIR /app

COPY pyproject.toml poetry.lock .
RUN /etc/poetry/bin/poetry config virtualenvs.create false && \
    /etc/poetry/bin/poetry install
COPY . .
ARG FLAG
RUN sed -i "s/NEEDCHANGE/`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`/g" /app/database/init.sql && \
    sed -i "s/FLAG/$FLAG/g" /app/database/init.sql
RUN chown -R daemon:daemon /app/database && chmod 770 /app/database

USER daemon 
ENTRYPOINT ["python", "/app/main.py"]
