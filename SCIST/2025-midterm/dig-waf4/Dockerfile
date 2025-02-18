FROM php:7-apache



RUN apt update && \
    apt install -qy dnsutils && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 555 /var/www/html && \
    mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" && \
    echo "environment[SHELL] = /bin/bash" >> "$PHP_INI_DIR/php.ini"

ARG FLAG
RUN echo $FLAG > /flag_`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`


COPY ./src /var/www/html

USER www-data
