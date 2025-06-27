# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 3
timeout = 60
loglevel = "info"
accesslog = "-"
errorlog = "-"
