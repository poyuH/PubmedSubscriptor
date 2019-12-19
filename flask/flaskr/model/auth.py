from passlib.hash import sha256_crypt
from . import db

PWD ='pwd'
EMAIL = 'email'
TAGS = 'tags'
USER = 'User'
SUCCESS = 'success'

def register(email, pwd, tags=[]):
    """
    return 'success' if successfully register, return error if fail
    """
    pubmed_db = db.get_db()
    users = pubmed_db[USER]
    query = {EMAIL: email}
    error = SUCCESS

    if users.find(query) == 1:
        error = 'Email {} is already registered.'.format(email)

    if error == SUCCESS:
        password = sha256_crypt.encrypt(pwd)
        document = {EMAIL:email, PWD:password, TAGS: tags}
        users.insert_one(document)
    return error

def login(email, pwd):
    """
    return 'success' if successfully register, return error if fail
    """
    pubmed_db = db.get_db()
    users = pubmed_db[USER]
    query = {EMAIL: email}
    error = 'Incorrect email or password.'

    result = users.find_one(query)
    if result and sha256_crypt.verify(pwd, result[PWD]):
        error = SUCCESS
    return error
