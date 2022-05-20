from flask import Flask
import zipfile
from io import StringIO
from io import BytesIO
from PIL import Image
import threading
import imghdr
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import queue
import os
import requests
from flask import request
from flask import redirect
from flask import url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'C:/Users/shrey/Pictures/Saved Pictures'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


PASSWORD = 0x71
executor = ThreadPoolExecutor(max_workers=4)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'zip'}

def decrypt(name,PASSWORD):
    enc_imag = f = open(f'test_enc/{name}', "rb")
    data = bytearray(enc_imag.read())
    for index, byte in enumerate(data):
        data[index] = byte ^ PASSWORD
    image = Image.open(BytesIO(data))
    image.show()
  

def thread_function(data, password, name):
    f = open(f'test_enc/{name}', "wb")
    for index, byte in enumerate(data):
        data[index] = byte ^ PASSWORD
    f.write(data)
    f.close()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def is_zip(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'





@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print(request.files)
            return "error no file"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return "error no file"
        filename = file.filename
        if file and allowed_file(filename):
            if (not is_zip(filename)):
                data = bytearray(file.read())
                thread_function(data,PASSWORD,filename)
                return "saved"
            zippedImgs = zipfile.ZipFile(file,mode='r')
            if (not os.path.exists('test_enc')):
                os.mkdir('test_enc')
            futures = []
            for i in range(len(zippedImgs.namelist())):
                file_in_zip = zippedImgs.namelist()[i]
                data = zippedImgs.read(file_in_zip)
                data = bytearray(data)
                file_in_zip = file_in_zip.split('/')
                future = executor.submit(thread_function, data, PASSWORD, file_in_zip[-1])
                futures.append(future)
            done, not_done = wait(futures, return_when=concurrent.futures.ALL_COMPLETED) 
            return "file saved"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''







    





          
    # print(done)