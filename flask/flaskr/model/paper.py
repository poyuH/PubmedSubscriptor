from . import db
from .. import global_values
from bson.objectid import ObjectId
from collections import defaultdict

USER = global_values.User.USER.value
EMAIL = global_values.User.EMAIL.value
STRMS = global_values.User.STRMS.value
PAPER = global_values.Paper.PAPER.value
ABSTRACT = global_values.Paper.ABSTRACT.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
TITLE = global_values.Paper.TITLE.value
PMID = global_values.Paper.PMID.value
URL = global_values.Database.URL.value
SUCCESS = global_values.Database.SUCCESS.value
STRM = global_values.SearchTerm.STRM.value
PAPERS = global_values.SearchTerm.PAPERS.value
ID = global_values.Database.ID.value

def get_user_search_terms(email):
    """
    get ObjectId of tags based on email
    """
    pubmed_db = db.get_db()
    users_col = pubmed_db[USER]
    query = {EMAIL:email}
    search_terms = users_col.find_one(query)[STRMS]
    return search_terms

def get_papers(search_terms):
    """
    get papers based on ObjectId of tags
    """
    pubmed_db = db.get_db()
    strm_col = pubmed_db[STRM]
    papers_col = pubmed_db[PAPER]
    context = defaultdict(list)
    for term in search_terms:
        query = {ID: term}
        for result in strm_col.find(query):
            for paper_id in result[PAPERS]:
                paper = papers_col.find_one({ID: paper_id})
                context[ID].append(paper_id)
                context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + paper[PMID])
                context[ABSTRACT].append(paper[ABSTRACT])
                context[TITLE].append(paper[TITLE])
                context[PUB_DATE].append(paper[PUB_DATE])
                context[JOURNAL].append(paper[JOURNAL])
    return context


