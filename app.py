from flask import Flask, render_template, request
from flask_mysqldb import MySQL

from video import extractImages

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
    return render_template('index.html')


@app.route('/upload', methods = ['POST'])
def upload():
    if request.method == 'POST':   
        print(request)
        f = request.files['file'] 
        f.save(f.filename)  

        extractImages(f.filename, "frames")

        return "aaa"   

