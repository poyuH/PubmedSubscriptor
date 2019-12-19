import os
# accessible as a variable in index.html:
from flask import Flask, request, render_template, redirect, Response
from . import auth


def create_app(test_config=None):
    # create and configure the app
    tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, instance_relative_config=True, template_folder=tmpl_dir)

    # 2019/11/8
    app.secret_key = os.urandom(24)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register home page as blueprint
    # app.register_blueprint(index.bp)
    app.register_blueprint(auth.bp)
    app.add_url_rule('/', endpoint='index')

    return app

