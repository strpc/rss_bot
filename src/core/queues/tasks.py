from src.core.queues.app import app


@app.task()
def run_chain():
    chain = load_new_articles.s() | send_new_articles.s()
    chain()


@app.task()
def load_new_articles():
    pass


@app.task()
def send_new_articles():
    pass
