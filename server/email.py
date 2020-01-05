from redis import Redis
from rq import Queue
from collections import defaultdict
import time

def test(x):
    return x + x

def email(query):
    """
    parse up to n pubmed results with published date after date_after
    """
    jobs = []

    q = Queue(connection=Redis())
    for x in query:
        jobs.append(q.enqueue(test, x))

    while len(q) > 0:
        continue
    # TODO better solution?
    if not jobs[-1].result:
        time.sleep(2)
    context = defaultdict(list)
    for job in jobs:
        print(job.result)



if __name__ == '__main__':
    email(['holy', 'shit', 4, 1, 53, 2])
