FROM phpmyadmin@sha256:7ebeef41095cbe071a00e3c85c8b44309f110eee546c7b3a6d1fcfe259d58e59
RUN sed -ri 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf \
 && sed -ri 's/:80>/:8080>/' /etc/apache2/sites-available/000-default.conf \
 && printf 'ServerName phpmyadmin\nServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-enabled/recipe.conf
USER 33:33
COPY docker/phpmyadmin/config.user.inc.php /etc/phpmyadmin/config.user.inc.php
ENTRYPOINT ["apache2-foreground"]
CMD []
EXPOSE 8080
