import global_values, db
from collections import defaultdict
from datetime import datetime, timedelta

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
upper_limit_papers = 10

def delete_search_term_from_paper(paper_idx, search_term_idx, pubmed_db):
    paper_col = pubmed_db[PAPER]

    # delete papers which only associated with this search_term_idx
    query = {ID: paper_idx}
    search_term_ids = paper_col.find_one(query).get(STRMS)
    if search_term_idx in search_term_ids:
        search_term_ids.remove(search_term_idx)
    if len(search_term_ids) == 0:
        # delete paper
        paper_col.delete_one(query)
    else:
        # update paper
        paper_col.update_one(query, {'$set': {STRMS: search_term_ids}})

def add_paper_to_search_term(search_term_idx, context, min_date):
    """
    add paper to search_term_idx
    """
    pubmed_db = db.get_db()
    search_term_col = pubmed_db[STRM]
    paper_col = pubmed_db[PAPER]
    paper_ids = []

    # check if there is any paper in context
    if context.get(PMID):
        for i, pmid in enumerate(context.get(PMID)):
            # check if pmid already exist, then create list of objectid of pmid
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
            # update min_date
            if context.get(PUB_DATE)[i] >= min_date:
                min_date = context.get(PUB_DATE)[i]
        min_date = min_date + timedelta(days=1)
        query = {ID: search_term_idx}
        search_term_col.update_one(query, {"$set": {MINDATE:min_date}})

    for paper_idx in paper_ids:
        # update search term
        query = {ID: search_term_idx}
        old_paper_ids = search_term_col.find_one(query).get(PAPERS)
        if paper_idx not in old_paper_ids:
            if len(old_paper_ids) >= upper_limit_papers:
                new_paper_ids = old_paper_ids[1:] + [paper_idx]
                # delete papers that are excluded
                delete_search_term_from_paper(old_paper_ids[0], search_term_idx, pubmed_db)
            else:
                new_paper_ids = old_paper_ids + [paper_idx]
            search_term_col.update_one(query, {"$set": {PAPERS:new_paper_ids}})

        # add search term id into paper_col
        query = {ID: paper_idx}
        old_search_term_ids = paper_col.find_one(query).get(STRMS)
        if search_term_idx not in old_search_term_ids:
            new_search_term_ids = old_search_term_ids + [search_term_idx]
            paper_col.update_one(query, {"$set": {STRMS: new_search_term_ids}})

