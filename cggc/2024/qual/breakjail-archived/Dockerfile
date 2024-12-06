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
    useradd -m pyjail && \
    chown -R root:root /home/pyjail && \
    chmod -R 755 /home/pyjail

WORKDIR /home/pyjail

COPY ./share /home/pyjail
COPY ./xinetd /etc/xinetd.d/chal
COPY ./flag /good_flag_b1f9A1BD

CMD ["/usr/sbin/xinetd", "-dontfork"]
