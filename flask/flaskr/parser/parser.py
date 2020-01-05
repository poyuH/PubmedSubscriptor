from bs4 import BeautifulSoup as bs
from datetime import datetime
from .. import global_values
import requests, json, os, sys


ID = 'id'
BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
CNT = 'count'
ERROR = 'error'
PMID = global_values.Paper.PMID.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
ABSTRACT = global_values.Paper.ABSTRACT.value
TITLE = global_values.Paper.TITLE.value
API_RATE_LIMIT = 'API rate limit exceeded'
restart = 0

class APIRateLimitError(Exception):
    pass


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.txt'), 'r') as f:
    lines = [line.rstrip('\n') for line in f]
    APIKEY = lines[0]

def pmid_gen(query, date_after, retmax):
    """
    return upto retmax amount of PMID results
    """
    today = datetime.now().strftime("%Y/%m/%d")
    url = BASE + "esearch.fcgi?db=pubmed&api_key=%s&term=%s&retstart=%i&retmax=%i&mindate=%s&maxdate=%s&datetype=pdat" % (APIKEY, query, restart, retmax, date_after, today)
    soup = bs(requests.get(url).content, features='html.parser')
    for pmid in soup.findAll(ID):
        yield pmid.string

def get_metadata(pmid):
    """
    return metadata according to PMID
    """
    summary_url = BASE + "esummary.fcgi?db=pubmed&api_key=%s&id=%s&retmode=json" % (APIKEY, pmid)
    summary = json.loads(requests.get(summary_url).content.decode('utf-8'))
    db_dict = {PMID: pmid}
    db_keys = [JOURNAL, PUB_DATE, TITLE]
    keys = ['fulljournalname', 'sortpubdate', 'title']
    for i in range(3):
        try:
            db_dict[db_keys[i]] = summary.get('result').get(pmid).get(keys[i])
        except AttributeError:
            if summary.get(ERROR) == API_RATE_LIMIT:
                raise APIRateLimitError
            break
    sortpubdate = datetime.strptime(db_dict.get(PUB_DATE), '%Y/%m/%d %H:%M')
    db_dict[PUB_DATE] = sortpubdate
    return db_dict

def get_abstract(pmid):
    """
    return abstract according to PMID
    """
    abs_url = BASE + "efetch.fcgi?db=pubmed&api_key=%s&id=%s&rettype=abstract&retmode=text" % (APIKEY, pmid)
    try:
        abstract = requests.get(abs_url).content.decode('utf-8')
    except:
        e = sys.exc_info()[0]
        print(e)
    db_dict = {ABSTRACT: abstract, PMID: pmid}
    return db_dict

