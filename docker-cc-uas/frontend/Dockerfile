FROM php:apache
WORKDIR /var/www/html

COPY index.php .
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
EXPOSE 80
