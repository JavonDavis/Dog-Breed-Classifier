from flask import Flask, render_template, request, flash, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from detector import classify_breed
import os



app = Flask(__name__)
app.debug = True

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.secret_key = 'doggyclassy'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = 50 * 1024 * 24  # 50MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'image_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image_file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('classify_image',
                                    filename=filename))
    return render_template('main.html')


@app.route('/results/<filename>')
def classify_image(filename):
    full_path = app.config['UPLOAD_FOLDER'] + '/' + filename
    result = classify_breed(full_path)
    print(result)
    return render_template('results.html', filename=full_path, classification_result=result)


@app.route('/results/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)