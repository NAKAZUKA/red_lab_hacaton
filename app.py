from flask import Flask, request, redirect, url_for, render_template
import os
from andrax import generate_and_save_plots, safe_divide

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'static/results'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file_post():
    print('here')
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        if not os.path.exists(file_path):
            file.save(file_path)
        generate_and_save_plots(file_path, app.config['RESULT_FOLDER'])
        context = safe_divide()
        return redirect(url_for('result'), context=context)


@app.route('/result')
def result():
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True)
