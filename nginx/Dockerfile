FROM nginx:stable

RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /etc/nginx

CMD ["sh", "-c", "envsubst '$NGINX_PORT $WEB_PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"]
