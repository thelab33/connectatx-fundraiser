import multiprocessing, os
bind = os.getenv("BIND", "0.0.0.0:8000")
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv("THREADS", 2))
worker_class = "gthread"
timeout = int(os.getenv("TIMEOUT", 60))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", 30))
keepalive = int(os.getenv("KEEPALIVE", 5))
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOGLEVEL", "info")
preload_app = True
