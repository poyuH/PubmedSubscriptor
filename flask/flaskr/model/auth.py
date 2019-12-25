from passlib.hash import sha256_crypt
from . import db
from .. import global_values

PWD = global_values.User.PWD.value
EMAIL = global_values.User.EMAIL.value
STRMS = global_values.User.STRMS.value
USER = global_values.User.USER.value
SUCCESS = global_values.Database.SUCCESS.value

def register(email, pwd, search_terms=[]):
    """
    return 'success' if successfully register, return error if fail
    """
    pubmed_db = db.get_db()
    users = pubmed_db[USER]
    query = {EMAIL: email}
    error = SUCCESS

    print(users.count(query))
    if users.count(query) == 1:
        error = 'Email {} is already registered.'.format(email)

    if error == SUCCESS:
        password = sha256_crypt.encrypt(pwd)
        document = {EMAIL:email, PWD:password, STRMS: search_terms}
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
