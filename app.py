import re
from datetime import datetime
import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from subprocess import Popen

from video import extractImages

app = Flask(__name__, template_folder='templates')
app.static_folder = 'static'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'safety_helmet_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

month_names_id = [
    'Jan', 'Feb', 'Mar', 'Apr',
    'Mei', 'Jun', 'Jul', 'Ags',
    'Sep', 'Okt', 'Nov', 'Des'
]


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

    cur_detection = request.args.get('detection')
    cur_image = request.args.get('image')
    cur_date = ''
    if cur_detection is not None:
        cur_path = 'frames/' + cur_detection + "/result/" + cur_image
        pattern = r'\d+'
        match = re.search(pattern, cur_image)
        seconds = int(match.group())
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        duration = '{:02}:{:02}'.format(minutes, seconds)
        if hours > 0:
            duration = '{:02}:{}'.format(hours, duration)
        cur_duration = duration
    else:
        cur_path = ''
        cur_duration = ''

    for detection in detections:
        path = 'static/frames/' + str(detection["id"]) + "/result"
        detection["images"] = []
        images = os.listdir(path)
        detection["date"] = detection["created_at"].strftime('%d %B %Y - %H:%M').replace(detection["created_at"].strftime('%B'), month_names_id[detection["created_at"].month - 1])
        if str(detection["id"]) == cur_detection:
            cur_date = detection["date"]

        for image in images:
            if '.jpg' in image:
                pattern = r'\d+'
                match = re.search(pattern, image)
                seconds = int(match.group())
                hours = seconds // 3600
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60
                duration = '{:02}:{:02}'.format(minutes, seconds)
                if hours > 0:
                    duration = '{:02}:{}'.format(hours, duration)
                detection["images"].append({'path': image, 'duration': duration})

    return render_template('index.html', detections=detections, cur_path=cur_path, cur_date=cur_date, cur_duration=cur_duration)


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

        process = Popen(["python", "detect.py", '--source', 'static/frames/' + str(inserted_id), "--weights","last.pt", "--project", "static/frames", "--name", str(inserted_id) + "/result", "--no-trace", "--save-txt"], shell=False)
        process.communicate()
        process.wait()

        return redirect('/')


        #
        # print("adadada")
        #
        # return "aaa"

@app.route('/delete/<string:detection_id>/<string:image>', methods = ['GET'])
def delete(detection_id, image):
    if request.method == 'GET':
        path = "static/frames/" + detection_id
        os.remove(path + "/" + image)
        os.remove(path + "/result/" + image)

        files = os.listdir(path)
        if len(files) <= 1:
            con = mysql.connection
            cur = con.cursor()
            cur.execute("DELETE FROM `detections` WHERE id = " + detection_id + ";")
            con.commit()
            cur.close()

        return redirect('/')