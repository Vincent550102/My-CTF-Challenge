FROM python:3.9

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
