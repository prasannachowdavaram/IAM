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
import pymysql

DB_SERVER_NAME = "assetmgt.crhg2bgmpsj5.us-east-2.rds.amazonaws.com"
USERNAME = "prasanna"
PASSWORD = "prasanna"
ASSET_DB_NAME = "Assetdb"
INSERT_VENDOR_QUERY = "INSERT INTO vendor (vendor_name, street, city, state, zipcode, tel_no) " \
                      " VALUES('{vendor_name}', '{street}', '{city}', '{state}', '{zipcode}', '{tel_no}');";

INSERT_ASSET_QUERY = "INSERT INTO ASSETS (VENDOR_ID_FK, ASSET_TYPE_ID_FK,LOCATION_ID_FK, name, brand," \
"workingcondition, cost, image)" \
"VALUES((select VENDOR_ID from VENDOR where VENDOR_NAME= '{vendorname}')," \
"(SELECT ASSET_TYPE_ID FROM ASSET_TYPE WHERE NAME='{assettypename}')," \
"(SELECT LOCATION_ID FROM LOCATION WHERE NAME='{locationname}')," \
"'{name}', '{brand}', '{condition}','{cost}','');" 

DELETE_ASSET_QUERY = "DELETE FROM ASSETS WHERE ASSET_ID='{asset_id}';";

SHOW_ASSET_QUERY = "SELECT ASSETS.ASSET_ID,ASSETS.NAME AS ASSETNAME, ASSETS.BRAND,"\
"ASSETS.WORKINGCONDITION,VENDOR.VENDOR_NAME,ASSET_TYPE.NAME AS TYPE,"\
"LOCATION.NAME AS LOACTION,ASSETS.COST FROM ASSETS  JOIN  VENDOR ON "\
"VENDOR.VENDOR_ID=ASSETS.VENDOR_ID_FK  JOIN  ASSET_TYPE ON "\
"ASSET_TYPE.ASSET_TYPE_ID=ASSETS.ASSET_TYPE_ID_FK JOIN  LOCATION ON "\
"LOCATION.LOCATION_ID=ASSETS.LOCATION_ID_FK;"


# def init_search_path(connection, conn_record):
#     cursor = connection.cursor()
#     try:
#         cursor.execute('ALTER USER prasanna WITH DEFAULT_SCHEMA=db_access_admin;')
#     finally:
#         cursor.close()
mod = Flask(__name__)

#engine = create_engine('mssql+pymssql://chowdavaram:chowdavaram@DESKTOP-MIF9U3O\SQLEXPRESS:1433/IAM')
conn = pymysql.connect(DB_SERVER_NAME, USERNAME, PASSWORD, ASSET_DB_NAME)

#[vid,vname]=cursor.execute("select vendor_id,vendor_name from Assetdb.vendor;")
#print([vid,vname])
# pymysql = MySQL()

# app.config['MYSQL_DATABASE_USER'] = 'prasanna'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'prasanna'
# app.config['MYSQL_DATABASE_DB'] = 'assetdb'
# app.config['MYSQL_DATABASE_HOST'] = 'assetmgt.crhg2bgmpsj5.us-east-2.rds.amazonaws.com'
# mysql.init_app(app)
# conn = mysql.connect()

# cursor = conn.cursor()
#import pypyodbc
#connection = pypyodbc.connect('Driver={SQL Server};Server=.;Database=IAM;uid=prasanna;pwd=prasanna')

#engine = create_engine('mssql+pyodbc://{}:{}@IAM'.format("chowdavaram", "chowdavaram" ))
# event.listen(engine, 'connect', init_search_path)
#table = 'ASSETS'
# metadata = MetaData(bind=engine)
# con = engine.connect()

# # Add all the table names here.
 #assets = Table('IAM.ASSETS', metadata, autoload=True)

#print(engine.has_table(table, schema='chowdavaram'))

#df = read_sql_table(table, con=engine, schema="prasanna")

# Change these value if login credentials for admin user needs to be changed.
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'


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


@mod.route("/api/getassets", methods=['GET'])
def get_assets():
    cursor = conn.cursor()
    cursor.execute(SHOW_ASSET_QUERY)
    all_assets = []
    for row in cursor:
        all_assets.append(row)
    return json.dumps({'assets': all_assets})

@mod.route("/api/addassets", methods=['POST'])
def add_assets():
    if request.method == 'POST':
        data = request.get_json()
        mod.logger.info(data)
        query = INSERT_ASSET_QUERY.format(name=data['name'],brand=data["brand"],
            condition=data["condition"],vendorname=data["vendor_name"],
            assettypename=data["asset_type_name"],locationname=data["location_name"],
            cost=data["cost"], image="")
        mod.logger.info(query)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return json.dumps({'response': 'success'})
    return json.dumps({'response': 'failed'})

@mod.route("/api/deleteassets", methods=['POST'])
def delete_assets():
    if request.method == 'POST':
        data = request.get_json()
        mod.logger.info(data)
        query = DELETE_ASSET_QUERY.format(asset_id=data['asset_id'])
        mod.logger.info(query)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return json.dumps({'response': 'success'})
    return json.dumps({'response': 'failed'})


# Callback to reload the user object. More details at
# https://flask-login.readthedocs.io/en/latest/#how-it-works.
@login_manager.user_loader
def load_user(userid):
    return User(userid)

if __name__ == "__main__":
    mod.run()
