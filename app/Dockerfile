FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ssl /app/ssl
COPY storyum /app/storyum
COPY users /app/users
COPY entrypoint.sh /app/entrypoint.sh
COPY gunicorn.py /app/gunicorn.py
COPY manage.py /app/manage.py

# WARNING: This file is not intended to be used in production.
COPY pytest.ini /app/pytest.ini

ENTRYPOINT ["/app/entrypoint.sh"]
