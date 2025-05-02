FROM nginx:stable

RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /etc/nginx

RUN rm /etc/nginx/conf.d/default.conf

CMD ["sh", "-c", "envsubst '$NGINX_PORT $NGINX_SSL_PORT $WEB_PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"]
