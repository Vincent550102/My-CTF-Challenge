FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY Dockerfile .
COPY templates/index.html ./templates/
COPY static/hint.jpg ./static/

ARG FLAG
RUN echo $FLAG > /flag_`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`

USER daemon 
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5050", "--debug"]