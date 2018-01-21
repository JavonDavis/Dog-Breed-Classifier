from flask import Flask, render_template, request, flash, redirect, send_from_directory, url_for, jsonify
from werkzeug.utils import secure_filename
from detector import classify_breed
import os



app = Flask(__name__)
app.debug = True
app.static_folder = 'static'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.secret_key = 'doggyclassy'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = 50 * 1024 * 1024  # 50MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return 'Please navigate to /home'


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

@app.route('/api/classify', methods=['POST'])
def api():
    result, error = None, None
    # check if the post request has the file part
    if 'image_file' not in request.files:
        error = 'No image_file parameter'
    else:
        file = request.files['image_file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            error = 'Filename is empty'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if not error:
            full_path = app.config['UPLOAD_FOLDER'] + '/' + file.filename
            result = classify_breed(full_path)
            print(result)
    return jsonify({'error': error, 'result': result})


@app.route('/results/<filename>')
def classify_image(filename):
    full_path = app.config['UPLOAD_FOLDER'] + '/' + filename
    result = classify_breed(full_path)
    print(result)
    return render_template('results.html', filename=full_path, classification_result=result['message'])


@app.route('/results/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
