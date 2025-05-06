FROM postgres:14

USER root

RUN mkdir -p /var/lib/postgresql/ssl \
    && chown postgres:postgres /var/lib/postgresql/ssl \
    && chmod 700 /var/lib/postgresql/ssl

COPY ssl/storyum_db.crt /var/lib/postgresql/ssl/storyum_db.crt
COPY ssl/storyum_db.key /var/lib/postgresql/ssl/storyum_db.key

RUN mkdir -p /etc/postgresql \
    && chown postgres:postgres /etc/postgresql

COPY conf/postgresql.conf /etc/postgresql/postgresql.conf
COPY conf/pg_hba.conf /etc/postgresql/pg_hba.conf

RUN chown postgres:postgres /etc/postgresql/postgresql.conf \
    && chown postgres:postgres /etc/postgresql/pg_hba.conf \
    && chown postgres:postgres /var/lib/postgresql/ssl/* \
    && chmod 600 /var/lib/postgresql/ssl/storyum_db.key

USER postgres

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
