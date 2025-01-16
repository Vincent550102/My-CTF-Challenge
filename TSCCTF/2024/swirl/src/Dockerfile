FROM php:7.4.33-apache

RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 555 /var/www/html

ARG FLAG
RUN echo $FLAG > /flag_`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`

USER www-data