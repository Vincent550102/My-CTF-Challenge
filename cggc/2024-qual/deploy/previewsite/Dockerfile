FROM tiangolo/uwsgi-nginx-flask:python3.10

RUN pip install --no-cache-dir requests

ARG FLAG
RUN echo $FLAG > /flag
