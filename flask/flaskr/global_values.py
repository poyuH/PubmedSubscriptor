from enum import Enum

class User(Enum):
    PWD = 'pwd'
    EMAIL = 'email'
    STRMS = 'search_terms'
    USER = 'User'

class Database(Enum):
    SUCCESS = 'success'
    ID = '_id'
    URL = 'url'

class Session(Enum):
    USER_ID = 'user_id'

class Paper(Enum):
    PAPER = 'Paper'
    PMID = 'PMID'
    JOURNAL = 'journal'
    PUB_DATE = 'publish_date'
    ABSTRACT = 'abstract'
    TITLE = 'title'

class SearchTerm(Enum):
    STRM = 'SearchTerm'
    PAPERS = 'papers'
    QUERY = 'query'
    MINDATE = 'min_date'
