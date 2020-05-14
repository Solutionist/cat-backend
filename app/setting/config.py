# CouchDB
db_user = 'admin'
db_password = 'admintest'
db_host = 'localhost'
db_port = '5984'

# Internal logging
filename = "../internal.log"
log_level = "logging.DEBUG"

# Gunicorn setting for production
# IP/Port
g_host = "0.0.0.0"
g_port = 7777
bind = '{}:{}'.format(g_host, g_port)
backlog = 2048

# worker
workers = 1
timeout = 30
keepalive = 2
worker_class = 'uvicorn.workers.UvicornWorker'

# daemon
daemon = True

# logging
errorlog = '../api.log'
loglevel = 'debug'
capture_output = True
