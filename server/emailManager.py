from redis import Redis
from rq import Queue
from collections import defaultdict
from datetime import datetime
import time, smtplib, ssl
import db
import parser, global_values, paper

PORT = 465
SENDER = "pubmedsubscription@gmail.com"
USER = global_values.User.USER.value
EMAIL = 'email'
STRMS = 'search_terms'
STRM = global_values.SearchTerm.STRM.value
MINDATE = 'min_date'
QUERY = 'query'
ID = '_id'
retmax = 100


JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
ABSTRACT = global_values.Paper.ABSTRACT.value
TITLE = global_values.Paper.TITLE.value
PMID = global_values.Paper.PMID.value

def send_email(receiver, message):
    # TODO skip 1@gmail and 2@gmail
    if receiver in ['1@gmail.com', '2@gmail.com']:
        return

    with open('email_secret.txt', 'r') as f:
        password = f.read()
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
        server.login(SENDER, password)
        message = """\
        Subject: Hi there

This message is sent from Python."""
        server.sendmail(SENDER, receiver, message)

def send_daily_updates():
    jobs = []
    q = Queue(connection=Redis())
    db.start()
    users_col = db.db[USER]
    search_term_col = db.db[STRM]
    users = db.get_all_users()
    for user in users:
        receiver = user[EMAIL]
        search_terms_ids = user[STRMS]
        print(receiver)
        for search_term_idx in search_terms_ids:
            result = search_term_col.find_one({ID: search_term_idx})
            min_date = result[MINDATE]
            search_term = result[QUERY]
            print(search_term + '==========================')
            paper_dict = defaultdict(list)
            for pmid in parser.pmid_gen(search_term, min_date.strftime("%Y/%m/%d"), retmax):
                result = parser.get_metadata(pmid)
                abstract = parser.get_abstract(pmid)
                paper_dict[ABSTRACT].append(abstract)
                paper_dict[JOURNAL].append(result.get(JOURNAL))
                paper_dict[PUB_DATE].append(result.get(PUB_DATE))
                paper_dict[TITLE].append(result.get(TITLE))
                paper_dict[PMID].append(pmid)
                print(paper_dict[TITLE])
            # add pmid to database
            print('min_date', min_date)
            paper.add_paper_to_search_term(search_term_idx, paper_dict, min_date, db.db)
            # TODO add email, email with abstract

"""
       jobs.append(q.enqueue(send_email, receiver))
    while len(q) > 0:
        continue
    # TODO better solution?
    if not jobs[-1].result:
        time.sleep(2)
    context = defaultdict(list)
    print('finish')
    """


if __name__ == '__main__':
    # send_email("poyu0987@gmail.com")
    send_daily_updates()
