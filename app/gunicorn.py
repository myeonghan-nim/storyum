import multiprocessing
import os
import ssl

from dotenv import load_dotenv

load_dotenv()

bind = "0.0.0.0:8000"

workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1024))
max_requests_jitter = 256

timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))

keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

certfile = os.getenv("GUNICORN_CERTFILE")
keyfile = os.getenv("GUNICORN_KEYFILE")
ssl_version = ssl.PROTOCOL_TLSv1_2

# TODO: logging
# accesslog = "-"
# errorlog = "-"
# loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
