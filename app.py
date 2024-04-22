import os

from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from subprocess import Popen

from video import extractImages

app = Flask(__name__, template_folder='templates')
app.static_folder = 'static'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'safety_helmet_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/login')
def login():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM users LIMIT 1""")
    rv = cur.fetchall()
    cur.close()
    return render_template('login.html')


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM detections""")
    detections = cur.fetchall()
    cur.close()

    return render_template('index.html', detections=detections)


@app.route('/upload', methods = ['POST'])
def upload():
    if request.method == 'POST':
        con = mysql.connection
        cur = con.cursor()
        cur.execute("""INSERT INTO `detections` (`id`, `workers`, `violations`, `duration`, `created_at`, `updated_at`) VALUES (NULL, '1', '2', '3', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);""")
        con.commit()
        cur.close()

        inserted_id = cur.lastrowid
        f = request.files['file']
        path = 'static/frames/' + str(inserted_id)
        os.mkdir(path)

        f.save('temp/' + f.filename)

        extractImages('temp/' + f.filename, path)

        os.remove('temp/' + f.filename)

        return redirect('/')

        # process = Popen(["python", "detect.py", '--source', "frame0.jpg", "--weights","last.pt"], shell=False)
        # process.communicate()
        # process.wait()
        #
        # print("adadada")
        #
        # return "aaa"

