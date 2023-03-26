from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from collections import defaultdict
from urllib.parse import urlencode, parse_qs
import os
import google_vision_api
import ast

app = Flask(__name__)


# FOR ACTUAL USE
@app.route('/upload_file_for_payload', methods = ['POST'])
def upload_file_for_payload():
    f = request.files['file']
    file_name = os.path.abspath('resources/' + secure_filename(f.filename))
    f.save(file_name)
    # IMPT PART
    payload = google_vision_api.run_pipeline(file_name)
    return payload


# DEMO PURPOSES
@app.route('/')
def render_upload_file():
    return render_template('Upload.html')


@app.route('/upload_single', methods = ['POST'])
def upload_file():
    f = request.files['file']
    file_name = os.path.abspath('resources/' + secure_filename(f.filename))
    f.save(file_name)
    # IMPT PART
    payload = google_vision_api.run_pipeline(file_name)
    return redirect(url_for('on_successful_upload', result = urlencode(payload)))


@app.route('/upload_multiple', methods = ['POST'])
def upload_multiple_files():
    files = request.files.getlist('file')
    payload = {}
    for f in files:
        file_name = os.path.abspath('resources/' + secure_filename(f.filename))
        f.save(file_name)
        # IMPT PART
        payload[secure_filename(f.filename)] = google_vision_api.run_pipeline(file_name)
    return redirect(url_for('on_successful_uploads', result = urlencode(payload)))


@app.route('/successful_upload/<result>')
def on_successful_upload(result):
    result = parse_qs(result)
    result = {k: ast.literal_eval(v[0]) for k, v in result.items()}
    print(f"result:\n{result}")
    print()
    return render_template('SuccessfulUpload.html', result = result)


@app.route('/successful_uploads/<result>')
def on_successful_uploads(result):
    result = parse_qs(result)
    result = {k: ast.literal_eval(v[0]) for k, v in result.items()}
    print(f"result:\n{result}")
    print()
    return render_template('SuccessfulUploadMultiple.html', result = result)
# END OF DEMO PURPOSES


if __name__ == '__main__':
   app.run(debug = True)