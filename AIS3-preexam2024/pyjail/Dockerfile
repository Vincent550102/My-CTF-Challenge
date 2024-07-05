# Use Python base image with specific hash for reliability
FROM python:3.10.14@sha256:f68383667ffe53e85cc0fe4f5a604d303dfa364f238ac37a4675980a2b93b1c5

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

# Command to start xinetd without forking
CMD ["/usr/sbin/xinetd", "-dontfork"]

