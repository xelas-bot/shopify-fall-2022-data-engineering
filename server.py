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

PASSWORD = 0x71
executor = ThreadPoolExecutor(max_workers=4)

def decrypt(name,PASSWORD):
    enc_imag = f = open(f'test_enc/{name}', "rb")
    data = bytearray(enc_imag.read())
    for index, byte in enumerate(data):
        data[index] = byte ^ PASSWORD
    image = Image.open(BytesIO(data))
    image.show()
  

def thread_function(data, password, name):
    print(name)
    f = open(f'test_enc/{name}', "wb")
    for index, byte in enumerate(data):
        data[index] = byte ^ PASSWORD
    f.write(data)
    f.close()





# zippedImgs = zipfile.ZipFile('test.zip',mode='r')
# if (not os.path.exists('test_enc')):
#     os.mkdir('test_enc')
# futures = []
# for i in range(len(zippedImgs.namelist())):
#     print ("iter", i, " ")
#     file_in_zip = zippedImgs.namelist()[i]
#     data = zippedImgs.read(file_in_zip)
#     data = bytearray(data)
#     file_in_zip = file_in_zip.split('/')
#     future = executor.submit(thread_function, data, PASSWORD, file_in_zip[-1])
#     futures.append(future)


# done, not_done = wait(futures, return_when=concurrent.futures.ALL_COMPLETED)       
# print(done)
decrypt("chic.PNG",PASSWORD)