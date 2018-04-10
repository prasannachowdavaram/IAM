import os
from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import url_for
from flask import Response
from flask import send_from_directory
from flask_login import LoginManager, UserMixin, \
login_required, login_user, logout_user, current_user

from sqlalchemy import create_engine, MetaData, Table
import json

from pandas import read_sql_table

from sqlalchemy import event

from flask import jsonify
import os
from flask_cors import CORS, cross_origin

# def init_search_path(connection, conn_record):
#     cursor = connection.cursor()
#     try:
#         cursor.execute('ALTER USER prasanna WITH DEFAULT_SCHEMA=db_access_admin;')
#     finally:
#         cursor.close()

#engine = create_engine('mssql+pymssql://chowdavaram:chowdavaram@DESKTOP-MIF9U3O\SQLEXPRESS:1433/IAM')



import sqlalchemy as sa
engine = sa.create_engine('mssql+pyodbc://DESKTOP-MIF9U3O\SQLEXPRESS/IAM')

#engine = create_engine('mssql+pyodbc://{}:{}@IAM'.format("chowdavaram", "chowdavaram" ))
# event.listen(engine, 'connect', init_search_path)
table = 'ASSETS'
# metadata = MetaData(bind=engine)
# con = engine.connect()

# # Add all the table names here.
 #assets = Table('IAM.ASSETS', metadata, autoload=True)

#print(engine.has_table(table, schema='chowdavaram'))

df = read_sql_table(table, con=engine, schema="prasanna")

# Change these value if login credentials for admin user needs to be changed.
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'


mod = Flask(__name__)

# Using this to fix CORS issue because the client(angular)
# runs on a different port compared to the server(flask)
CORS(mod)

# config
mod.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)


@mod.route('/api/data')
def get_data():
    data = [
        {'Name': 'Mark', 'Role': 'Admin', 'Status': 'Active'},
        {'Name': 'Jacob', 'Role': 'Publisher', 'Status': 'Active'},
        {'Name': 'Paula', 'Role': 'Reviewer', 'Status': 'Active'},
        {'Name': 'Mary', 'Role': 'Reviewer', 'Status': 'Inactive'},
    ]
    return jsonify(data)

# flask-login
login_manager = LoginManager()
login_manager.init_app(mod)

# Basic user model. Just supports admin.
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = ADMIN_USERNAME
        self.password = ADMIN_PASSWORD

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

@mod.route("/login", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            user = User(1)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Wrong Credentials"
    return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')

@mod.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return send_from_directory("./mod/", "index.html")


@mod.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


@mod.route("/api/assets", methods=['GET'])
def get_assets():
    # Both of the queries below does the same thing.
    # assets.select(assets.c.id == 1).execute().first()
    # r = engine.execute('select * from assets where id = :1', [1]).first()
    return json.dumps({'id': 'test_response'})

@mod.route("/api/addassets", methods=['POST'])
def add_assets():
    if request.method == 'POST':
        # r = engine.execute('INSERT * from assets where id = :1', [1]).first()
        return json.dumps({'response': 'success'})
    return json.dumps({'response': 'failed'})


# Callback to reload the user object. More details at
# https://flask-login.readthedocs.io/en/latest/#how-it-works.
@login_manager.user_loader
def load_user(userid):
    return User(userid)

if __name__ == "__main__":
    mod.run()
