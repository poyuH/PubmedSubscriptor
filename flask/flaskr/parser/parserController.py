from .parser import pmid_gen, get_metadata, APIRateLimitError
from .. import global_values
from collections import defaultdict, deque
import time

PMID = global_values.Paper.PMID.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
ABSTRACT = global_values.Paper.ABSTRACT.value
TITLE = global_values.Paper.TITLE.value
URL = global_values.Database.URL.value

def parse_search_results(query, date_after, n=10):
    """
    parse up to n pubmed results with published date after date_after
    """
    context = defaultdict(list)
    q = deque([])
    while True:
        try:
            for pmid in pmid_gen(query, date_after, n):
                print(pmid)
                q.append(pmid)
            break
        except APIRateLimitError:
            print('fail')
            time.sleep(1)
            continue
        except:
            break
    while q:
        pmid = q.popleft()
        print('try', pmid)
        try:
            result_dict = get_metadata(pmid)
            context[PMID].append(result_dict.get(PMID))
            context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + result_dict.get(PMID))
            context[TITLE].append(result_dict.get(TITLE))
            context[PUB_DATE].append(result_dict.get(PUB_DATE))
            context[JOURNAL].append(result_dict.get(JOURNAL))
            context[ABSTRACT].append(result_dict.get(ABSTRACT))
        except APIRateLimitError:
            print('fail', pmid)
            time.sleep(1)
            q.appendleft(pmid)
        except:
            break
    return context

if __name__ == '__main__':
    print(parse_search_results('"dermatitis"[MeSH Terms] AND "fever"[MeSH Terms]', '2018/12/24'))
