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
from flask import send_file
import time
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'C:/Users/shrey/Pictures/Saved Pictures'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 1000 #max file size able to be recieved
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


PASSWORD_OFFSET = 0x71 # This is the offset from the user password we use
executor = ThreadPoolExecutor(max_workers=8)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'zip'}

def decrypt(name: str, password: int, user: str) -> Image:
    enc_imag = f = open(f'database/{user}/{name}', "rb")
    data = bytearray(enc_imag.read())
    password = (password + PASSWORD_OFFSET) % 0xFF
    password = password.to_bytes(1,'big')[0]
    for index, byte in enumerate(data):
        data[index] = byte ^ password
    


    try:
        image = Image.open(BytesIO(data))
        return image
    except: # if Image.open throws an error it means the image bytes are (purposefully) corrupted
        return Image.new('RGB', (100, 100))


def thread_function_encrypt(data: zipfile, password: int, name: str, user: str) -> None:
    # time.sleep(0.25) # for testing purposes
    f = open(f'database/{user}/{name.split("/")[-1]}', "wb")
    data = data.read(name)
    data = bytearray(data)
    password = (password + PASSWORD_OFFSET) % 0xFF
    password = password.to_bytes(1,'big')[0]
    for index, byte in enumerate(data):
        data[index] = byte ^ password
    f.write(data)
    f.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def is_zip(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    startTime = time.time()
    user = None
    password = None
    if ('username' in request.headers):
        user = str(request.headers['username'])
    else:
        return "Enter username"
    if ('password' in request.headers):
        password = int(request.headers['password'])
    else:
        return "Enter Password"

    
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
            # if file is single image then just run thread function synchronously
            if (not is_zip(filename)):
                thread_function_encrypt(file,password,filename)
                return "saved"
            zippedImgs = zipfile.ZipFile(file,mode='r')
            if (not os.path.exists('database')):
                os.mkdir('database')
            if (not os.path.exists(f'database/{user}')):
                os.mkdir(f'database/{user}')
            futures = []
            for i in range(len(zippedImgs.namelist())):
                file_in_zip = zippedImgs.namelist()[i]
                if (not allowed_file(file_in_zip)):
                    continue
                future = executor.submit(thread_function_encrypt, zippedImgs, password, file_in_zip, user)
                futures.append(future)
            
            done, not_done = wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            print(done)
            executionTime = (time.time() - startTime)
            print('Execution time in seconds: ' + str(executionTime))
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


@app.route('/retrieve', methods=['GET'])
def retrieve_image():

    # search for image user is looking for
    # get password for user
    # decrypt image using password + offset
    # send image back
    user = None
    password = None
    img_request = None
    if ('username' in request.headers):
        user = str(request.headers['username'])
    else:
        return "Enter username"
    if ('password' in request.headers):
        password = int(request.headers['password'])
    else:
        return "Enter Password"
    if ('img_name' in request.headers):
        img_request = str(request.headers['img_name'])
    else:
        return "Please specify an Image"
    
    # check if user + image exists in "database"
    if (not os.path.isfile(f'database/{user}/{img_request}') ):
        return "Image could not be located in secure database!"


    image_format = img_request.split('.')[-1]
    if (image_format == 'jpg'): # jpg extension is super annoying!
        image_format = 'jpeg'
    img = decrypt(img_request, password, user)
    img_io = BytesIO()
    img.save(img_io, image_format)
    img_io.seek(0)
    return send_file(img_io, mimetype=f'image/{image_format}')