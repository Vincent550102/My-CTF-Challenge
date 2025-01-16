FROM php:7.4.33-apache

COPY . /var/www/html

RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 555 /var/www/html && \
    chown www-data:www-data /var/www/html/upload && \
    chmod 775 /var/www/html/upload

ARG FLAG
RUN echo $FLAG > /flag-`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`

RUN echo "AddType application/x-httpd-php .php .Php .pHp .phP .pHP .PHp .PHP" >>/etc/apache2/apache2.conf
USER www-data