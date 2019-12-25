from redis import Redis
from rq import Connection, Worker, requeue_job

class APIRateLimitError(Exception):
    """Raise when reach API rate limit"""
    pass

def retry_handler(job, exc_type, exception, traceback):
    if isinstance(exception, APIRateLimitError):
        requeue_job(job.id, Redis())
        return False

def start_worker():
    with Connection():
        qs = ['default']
        w = Worker(qs)
        w.push_exc_handler(retry_handler)
        w.work()

if __name__ == '__main__':
    start_worker()
