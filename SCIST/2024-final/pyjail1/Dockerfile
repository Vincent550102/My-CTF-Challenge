FROM python:3.11-bullseye

# Update system, install xinetd, set up user and permissions
RUN apt-get update && \
    apt-get install -qy xinetd && \
    useradd -m pyjail && \
    chown -R root:root /home/pyjail && \
    chmod -R 755 /home/pyjail

# Set the working directory
WORKDIR /home/pyjail

# Copy the challenge files and xinetd configuration
COPY ./share /home/pyjail
COPY ./xinetd /etc/xinetd.d/chal
COPY ./flag /flag_432rdeoibhedqnjd

# Command to start xinetd without forking
CMD ["/usr/sbin/xinetd", "-dontfork"]
