FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY storyum /app/storyum
COPY entrypoint.sh /app/entrypoint.sh
COPY gunicorn.py /app/gunicorn.py
COPY manage.py /app/manage.py

ENTRYPOINT ["/app/entrypoint.sh"]
