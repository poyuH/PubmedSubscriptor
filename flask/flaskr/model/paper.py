from . import db
from .. import global_values
from bson.objectid import ObjectId
from collections import defaultdict

USER = global_values.User.USER.value
EMAIL = global_values.User.EMAIL.value
TAGS = global_values.User.TAGS.value
PAPER = global_values.Paper.PAPER.value
ABSTRACT = global_values.Paper.ABSTRACT.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
TITLE = global_values.Paper.TITLE.value
PMID = global_values.Paper.PMID.value
URL = global_values.Database.URL.value
SUCCESS = global_values.Database.SUCCESS.value
TAG = global_values.Tag.TAG.value
PAPERS = global_values.Tag.PAPERS.value
ID = global_values.Database.ID.value

def get_paper_tags(paper_id):
    """
    get ObjectId of tags based on ObjectId of paper
    """
    pubmed_db = db.get_db()
    papers_col = pubmed_db[PAPER]
    query = {ID:paper_id}
    tags = papers_col.find_one(query)[TAGS]
    return tags

def get_user_tags(email):
    """
    get ObjectId of tags based on email
    """
    pubmed_db = db.get_db()
    users_col = pubmed_db[USER]
    query = {EMAIL:email}
    tags = users_col.find_one(query)[TAGS]
    print('get_user_tags', tags)
    return tags

def get_papers(tags):
    """
    get papers based on ObjectId of tags
    """
    pubmed_db = db.get_db()
    tags_col = pubmed_db[TAG]
    papers_col = pubmed_db[PAPER]
    context = defaultdict(list)
    for tag in tags:
        query = {ID: tag}
        for result in tags_col.find(query):
            for paper_id in result[PAPERS]:
                paper = papers_col.find_one({ID: paper_id})
                context[ID].append(paper_id)
                context[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + paper[PMID])
                context[ABSTRACT].append(paper[ABSTRACT])
                context[TITLE].append(paper[TITLE])
                context[PUB_DATE].append(paper[PUB_DATE])
                context[JOURNAL].append(paper[JOURNAL])

    print('get_papers', context)
    return context


