FROM php@sha256:060ed9c0f6e4bbe4f8b25a34ca1ec596b96d8f4011cf7ee7eb6b7eecf01cb74f
RUN docker-php-ext-install pdo_mysql \
 && sed -ri 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf \
 && sed -ri 's/:80>/:8080>/' /etc/apache2/sites-available/000-default.conf \
 && mkdir -p /var/log/recipe \
 && chown 33:33 /var/log/recipe \
 && printf 'ServerName recipe-app\nServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-enabled/recipe.conf
COPY php.ini /usr/local/etc/php/conf.d/recipe.ini
COPY logging.conf /etc/apache2/conf-enabled/zz-logging.conf
COPY --chown=33:33 src/ /var/www/html/
USER 33:33
EXPOSE 8080
