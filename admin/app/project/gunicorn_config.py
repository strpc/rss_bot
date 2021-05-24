import os


loglevel = os.getenv("LOGLEVEL", "INFO")
worker_class = "uvicorn.workers.UvicornWorker"
IP_ADDRESS = os.getenv("IP_ADDRESS", "0.0.0.0")
PORT = os.getenv("RSS_BOT_PORT")
bind = f"{IP_ADDRESS}:{PORT}"

workers = int(os.getenv("UVICORN_WORKERS", 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
