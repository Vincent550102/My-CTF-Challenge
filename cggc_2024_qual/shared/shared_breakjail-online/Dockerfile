FROM ubuntu:20.04

ENV TZ=Asia/Taipei \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update &&\
    apt-get install -qy xinetd wget build-essential gdb lcov pkg-config \
    libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
    lzma lzma-dev tk-dev uuid-dev zlib1g-dev &&\
    wget https://www.python.org/ftp/python/3.14.0/Python-3.14.0a1.tgz &&\
    tar zxvf Python-3.14.0a1.tgz &&\
    cd Python-3.14.0a1 &&\
    ./configure && make && make install &&\
    python3 -m pip install flask gunicorn &&\
    useradd -m breakjail && \
    chown -R root:root /home/breakjail && \
    chmod -R 755 /home/breakjail

WORKDIR /home/breakjail

COPY ./app /home/breakjail

ARG FLAG
RUN echo $FLAG > /flag_`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`


ENV FLASK_ENV=production


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
