from redis import Redis
from rq import Queue
from .parser import pmid_gen, parse_pmid
from .. import global_values
from collections import defaultdict
import time

PMID = global_values.Paper.PMID.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
ABSTRACT = global_values.Paper.ABSTRACT.value
TITLE = global_values.Paper.TITLE.value
URL = global_values.Database.URL.value

def parse_search_results(query, date_after, n=30):
    """
    parse up to n pubmed results with published date after date_after
    """
    jobs = []

    q = Queue(connection=Redis())
    for pmid in pmid_gen(query, date_after, n):
        jobs.append(q.enqueue(parse_pmid, pmid))

    while len(q) > 0:
        continue
    # TODO better solution?
    if not jobs[-1].result:
        time.sleep(2)
    context = defaultdict(list)
    for job in jobs:
        try:
            context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + job.result.get(PMID))
            context[TITLE].append(job.result.get(TITLE))
            context[PUB_DATE].append(job.result.get(PUB_DATE))
            context[JOURNAL].append(job.result.get(JOURNAL))
            context[ABSTRACT].append(job.result.get(ABSTRACT))
        except AttributeError:
            continue
    return context

if __name__ == '__main__':
    print(parse_search_results('"dermatitis"[MeSH Terms] AND "fever"[MeSH Terms]', '2018/12/24'))
