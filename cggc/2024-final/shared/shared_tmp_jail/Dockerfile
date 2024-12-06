FROM python:3.12.7@sha256:f2c6de139e92081c0181a6472e9d6f25f05b2ca1e8ede6b2375bb147fdabd32e AS base

RUN apt-get update && \
    apt-get install -qy xinetd && \
    useradd -m pyjail && \
    chown -R root:root /home/pyjail && \
    chmod -R 755 /home/pyjail

COPY --chmod=755 ./share /home/pyjail
COPY ./xinetd /etc/xinetd.d/chal

ARG FLAG
RUN echo $FLAG > /flag_`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`

CMD ["/usr/sbin/xinetd", "-dontfork"]
