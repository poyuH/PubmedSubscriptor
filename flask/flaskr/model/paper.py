from . import db
from .. import global_values
from bson.objectid import ObjectId
from collections import defaultdict
from datetime import datetime

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
MINDATE = global_values.SearchTerm.MINDATE.value
ID = global_values.Database.ID.value
PAPER_ID = 'paper' + ID
STRM_ID = 'search_term' + ID
BREAK_PTS = 'break_pts'


class TooManySearchTerms(Exception):
    pass

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
    outer_dict[BREAK_PTS].append(0)
    for i, idx in enumerate(search_term_ids):
        query = {ID: idx}
        outer_dict[STRM_ID].append(idx)
        outer_dict[STRMS].append(search_terms[i])
        for result in strm_col.find(query):
            for paper_id in result[PAPERS]:
                paper = papers_col.find_one({ID: paper_id})
                context[PAPER_ID].append(paper_id)
                context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + paper[PMID])
                context[ABSTRACT].append(paper.get(ABSTRACT))
                context[TITLE].append(paper.get(TITLE))
                context[PUB_DATE].append(paper.get(PUB_DATE).strftime("%Y-%m-%d"))
                context[JOURNAL].append(paper.get(JOURNAL))
                context[STRMS].append(search_terms[i])
        outer_dict[BREAK_PTS].append(len(context[URL]))
    context.update(outer_dict)
    return context

def delete_search_term(email, search_term_idx_string):
    """
    delete_search_terms based on SearchTerm objectid and email
    """
    search_term_idx = ObjectId(search_term_idx_string)
    pubmed_db = db.get_db()
    users_col = pubmed_db[USER]
    search_term_col = pubmed_db[STRM]
    paper_col = pubmed_db[PAPER]

    # delete from User
    query = {EMAIL: email}
    old_search_term_ids = users_col.find_one(query)[STRMS]
    old_search_term_ids.remove(search_term_idx)
    new_search_term_ids = {'$set': {STRMS: old_search_term_ids}}
    users_col.update_one(query, new_search_term_ids)

    # delete papers which only associated with this search_term_idx
    query = {ID: search_term_idx}
    for result in search_term_col.find(query):
        for old_paper_idx in result.get(PAPERS):
            old_paper = paper_col.find_one({ID: old_paper_idx})
            old_search_term_ids = old_paper.get(STRMS)
            old_search_term_ids.remove(search_term_idx)
            if len(old_search_term_ids) < 1:
                paper_col.delete_one({ID: old_paper_idx})
            else:
                new_search_term_ids = {'$set': {STRMS: old_search_term_ids}}
                paper_col.update_one({ID: old_paper_idx}, new_search_term_ids)
    # delete search_term_idx
    query = {ID: search_term_idx}
    search_term_col.delete_one(query)

def add_search_term(email, search_term, context):
    """
    add search_term to Database
    """
    pubmed_db = db.get_db()
    users_col = pubmed_db[USER]
    search_term_col = pubmed_db[STRM]
    paper_col = pubmed_db[PAPER]
    paper_ids = []
    # check if this email has too many search terms
    if len(users_col.find_one({EMAIL: email}).get(STRMS)) >= 5:
        raise TooManySearchTerms

    # check if there is any paper in context
    # check if pmid already exist, then create list of objectid of pmid
    if context.get(PMID):
        for i, pmid in enumerate(context.get(PMID)):
            result = paper_col.find_one({PMID: pmid})
            if result:
                paper_ids.append(result.get(ID))
            else:
                info = {}
                info[PMID] = pmid
                info[TITLE] = context.get(TITLE)[i]
                info[PUB_DATE] = context.get(PUB_DATE)[i]
                info[JOURNAL] = context.get(JOURNAL)[i]
                info[ABSTRACT] = context.get(ABSTRACT)[i]
                info[STRMS] = []
                paper_ids.append(paper_col.insert_one(info).inserted_id)
    # insert search term
    if context.get(PUB_DATE):
        min_date = context.get(PUB_DATE)[0]
    else:
        min_date = datetime.today()
    info = {PAPERS: paper_ids, QUERY: search_term, MINDATE: min_date}
    search_term_idx = search_term_col.insert_one(info).inserted_id

    # update user with current search term
    query = {EMAIL: email}
    old_search_term_ids = users_col.find_one(query).get(STRMS)
    new_search_term_ids = old_search_term_ids + [search_term_idx]
    users_col.update_one(query, {"$set": {STRMS: new_search_term_ids}})

    # add search term id into paper_col
    for paper_idx in paper_ids:
        query = {ID: paper_idx}
        old_search_term_ids = paper_col.find_one(query).get(STRMS)
        new_search_term_ids = old_search_term_ids + [search_term_idx]
        paper_col.update_one(query, {"$set": {STRMS: new_search_term_ids}})



