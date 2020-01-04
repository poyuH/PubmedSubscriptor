from redis import Redis
from rq import Queue
from .parser import pmid_gen, get_metadata
from .. import global_values
from collections import defaultdict
import time

PMID = global_values.Paper.PMID.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
ABSTRACT = global_values.Paper.ABSTRACT.value
TITLE = global_values.Paper.TITLE.value
URL = global_values.Database.URL.value


def parse_search_results_slow(query, date_after, n=10):
    """
    parse up to n pubmed results with published date after date_after
    """
    jobs = []

    q = Queue(connection=Redis())
    for pmid in pmid_gen(query, date_after, n):
        jobs.append(q.enqueue(get_metadata, pmid))

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


def parse_search_results(query, date_after, n=10):
    """
    parse up to n pubmed results with published date after date_after
    """
    context = defaultdict(list)
    for pmid in pmid_gen(query, date_after, n):
        result_dict = get_metadata(pmid)
        context[PMID].append(result_dict.get(PMID))
        context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + result_dict.get(PMID))
        context[TITLE].append(result_dict.get(TITLE))
        context[PUB_DATE].append(result_dict.get(PUB_DATE))
        context[JOURNAL].append(result_dict.get(JOURNAL))
        context[ABSTRACT].append(result_dict.get(ABSTRACT))
    return context

if __name__ == '__main__':
    print(parse_search_results('"dermatitis"[MeSH Terms] AND "fever"[MeSH Terms]', '2018/12/24'))
