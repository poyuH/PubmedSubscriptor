from enum import Enum

class User(Enum):
    PWD = 'pwd'
    EMAIL = 'email'
    TAGS = 'tags'
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
    TAGS = 'tags'

class Tag(Enum):
    TAG = 'Tag'
    PAPERS = 'papers'
    STR = 'string'
    NEW_DATE = 'newest_date'
