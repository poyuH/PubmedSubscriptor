from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for, g
)
from datetime import datetime
import functools
from .model import db, auth, paper
from .parser import parserController
from . import global_values

my_db = db
bp = Blueprint('controller', __name__)
SUCCESS = global_values.Database.SUCCESS.value
EMAIL = global_values.User.EMAIL.value
PWD = global_values.User.PWD.value
STRMS = global_values.User.STRMS.value
USER_ID = global_values.Session.USER_ID.value
PAPERS = global_values.SearchTerm.PAPERS.value
MINDATE = global_values.SearchTerm.MINDATE.value
CONTEXT = 'context'

# connects to our database
@bp.before_request
def before_request():
    my_db.start()

# close our database
@bp.teardown_request
def teardown_request(exception):
    my_db.close(exception)

@bp.route('/', methods=['GET', 'POST'])
def home_page():
    context = {}
    if request.method == 'POST':
        search_term = request.form.get(STRMS)
        mindate = request.form.get(MINDATE)
        if mindate:
            date_after = datetime.strptime(mindate, '%m/%d/%Y').strftime('%Y/%m/%d')
        else:
            date_after = "1800/01/01"
        context = parserController.parse_search_results(search_term, date_after)
        context[STRMS] = search_term
        context[MINDATE] = mindate
        session[CONTEXT] = context
        return render_template("index.html", **context)
    if g.user:
        context = session.get(CONTEXT)
        # TODO
        # search_terms = paper.get_user_search_terms(g.user)
        # context = paper.get_papers(search_terms)
    return render_template("index.html", **context)

@bp.route('/register', methods=['POST'])
def register():
    context = {}
    if request.method == 'POST':
        email = request.form[EMAIL]
        pwd = request.form[PWD]
        if not email:
            error = 'Email is required.'
        elif not pwd:
            error = 'Password is required.'
        error = auth.register(email, pwd)
        if error == SUCCESS:
            session[USER_ID] = email
            return redirect(url_for('controller.home_page'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=['POST'])
def login():
    context = {}
    if request.method == 'POST':
        email = request.form[EMAIL]
        pwd = request.form[PWD]
        if not email:
            error = 'Email is required.'
        elif not pwd:
            error = 'Password is required.'
        error = auth.login(email, pwd)
        if error == SUCCESS:
            session[USER_ID] = email
            return redirect(url_for('controller.home_page'))
        flash(error)
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('controller.home_page'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get(USER_ID)
    if user_id is None:
        g.user = None
    else:
        g.user = user_id

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view