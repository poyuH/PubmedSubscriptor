from redis import Redis
from rq import Queue
from collections import defaultdict
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time, smtplib, ssl
import db
import parser, global_values, alter_db

PORT = 465
retmax = 10
SENDER = "pubmedsubscription@gmail.com"
USER = global_values.User.USER.value
EMAIL = global_values.User.EMAIL.value
STRMS = global_values.User.STRMS.value
STRM = global_values.SearchTerm.STRM.value
MINDATE = global_values.SearchTerm.MINDATE.value
QUERY = global_values.SearchTerm.QUERY.value
ID = global_values.Database.ID.value
JOURNAL = global_values.Paper.JOURNAL.value
PUB_DATE = global_values.Paper.PUB_DATE.value
ABSTRACT = global_values.Paper.ABSTRACT.value
TITLE = global_values.Paper.TITLE.value
PMID = global_values.Paper.PMID.value
URL = global_values.Database.URL.value


def send_email(receiver, info):
    """
    send email to receiver based on info, which is a defaultdict(list)
    with title, pmid, etc
    """

    with open('email_secret.txt', 'r') as f:
        password = f.read()
    # Create a secure SSL context
    context = ssl.create_default_context()

    message = MIMEMultipart("alternative")
    message["Subject"] = "Pubmed Subscription - {}".format(datetime.today().strftime("%Y/%m/%d"))
    message["From"] = SENDER
    message["To"] = receiver

    # Create the plain-text and HTML version of your message
    text, html = "", ""

    for i, pmid in enumerate(info.get(PMID)):
        # Skip abstract for now
        text = text + info.get(TITLE)[i] + '\n' + info.get(URL)[i] + '\n' + info.get(PUB_DATE)[i].strftime('%Y-%m-%d') + '\n\n'
        html = html + "<a href={}>{}</a><br>publish date: {}<br><br>".format(
            info.get(URL)[i], info.get(TITLE)[i], info.get(PUB_DATE)[i].strftime('%Y-%m-%d')
        )

    text = """\
    Hi,
    This is the update for your Pubmed Subscriptions today.
    {}
    Have a great day""".format(text)
    html = """\
    <html>
      <body>
        <p>Hi,<br>
        This is the update for your Pubmed Subscriptions today.<br><br>
        {}
        </p>
      </body>
    </html>
    """.format(html)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
        server.login(SENDER, password)
        server.sendmail(SENDER, receiver, message.as_string())



def send_daily_updates():
    jobs = []
    q = Queue(connection=Redis())
    db.start()
    users_col = db.db[USER]
    search_term_col = db.db[STRM]
    users = []
    for user in users_col.find({}):
        users.append(user)
    for user in users:
        receiver = user[EMAIL]
        search_terms_ids = user[STRMS]
        for search_term_idx in search_terms_ids:
            result = search_term_col.find_one({ID: search_term_idx})
            min_date = result[MINDATE]
            search_term = result[QUERY]
            paper_dict = defaultdict(list)
            for pmid in parser.pmid_gen(search_term, min_date.strftime("%Y/%m/%d"), retmax):
                result = parser.get_metadata(pmid)
                abstract = parser.get_abstract(pmid)
                paper_dict[ABSTRACT].append(abstract)
                paper_dict[JOURNAL].append(result.get(JOURNAL))
                paper_dict[PUB_DATE].append(result.get(PUB_DATE))
                paper_dict[TITLE].append(result.get(TITLE))
                paper_dict[PMID].append(pmid)
                paper_dict[URL].append('https://www.ncbi.nlm.nih.gov/pubmed/' + pmid)
            # add pmid to database
            alter_db.add_paper_to_search_term(search_term_idx, paper_dict, min_date, db.db)
            # add email, email with abstract
            if paper_dict:
                send_email(receiver, paper_dict)

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
    send_daily_updates()
