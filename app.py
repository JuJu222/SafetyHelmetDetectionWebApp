from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates')
app.static_folder = 'static'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'safety_helmet_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM users LIMIT 1""")
    rv = cur.fetchall()
    cur.close()
    return rv[0]
    return render_template('index.html')
