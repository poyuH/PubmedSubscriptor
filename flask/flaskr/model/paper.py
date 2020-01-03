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
QUERY = global_values.SearchTerm.QUERY.value
ID = global_values.Database.ID.value
PAPER_ID = 'paper' + ID
STRM_ID = 'search_term' + ID

def get_user_search_terms(email):
    """
    get ObjectId of tags based on email
    """
    pubmed_db = db.get_db()
    users_col = pubmed_db[USER]
    search_term_col = pubmed_db[STRM]
    query = {EMAIL:email}
    search_term_ids = users_col.find_one(query)[STRMS]
    search_terms = []
    for idx in search_term_ids:
        search_terms.append(search_term_col.find_one({ID:idx})[QUERY])
    return search_term_ids, search_terms

def get_papers(search_term_ids, search_terms):
    """
    get papers based on ObjectId of tags
    """
    pubmed_db = db.get_db()
    strm_col = pubmed_db[STRM]
    papers_col = pubmed_db[PAPER]
    context = defaultdict(list)
    outer_dict = defaultdict(list)
    for i, idx in enumerate(search_term_ids):
        query = {ID: idx}
        outer_dict[STRM_ID].append(idx)
        outer_dict[STRMS].append(search_terms[i])
        for result in strm_col.find(query):
            for paper_id in result[PAPERS]:
                paper = papers_col.find_one({ID: paper_id})
                context[PAPER_ID].append(paper_id)
                context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + paper[PMID])
                context[ABSTRACT].append(paper[ABSTRACT])
                context[TITLE].append(paper[TITLE])
                context[PUB_DATE].append(paper[PUB_DATE].strftime("%Y-%m-%d"))
                context[JOURNAL].append(paper[JOURNAL])
                context[STRMS].append(search_terms[i])
        for key in context:
            context[key].append('break')
    context.update(outer_dict)
    return context

def delete_search_terms(search_term_idx):
    """
    delete_search_terms based on SearchTerm objectid
    """

