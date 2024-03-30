from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')
