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
from filecmp import cmp
from PIL import ImageChops

# Checks if images are equal based on qualitative factors (not raw content due to compression)
def are_images_equal(img1, img2):
    equal_size = img1.height == img2.height and img1.width == img2.width

    if img1.mode == img2.mode == "RGBA":
        img1_alphas = [pixel[3] for pixel in img1.getdata()]
        img2_alphas = [pixel[3] for pixel in img2.getdata()]
        equal_alphas = img1_alphas == img2_alphas
    else:
        equal_alphas = True

    equal_content = not ImageChops.difference(
        img1.convert("RGB"), img2.convert("RGB")
    ).getbbox()

    return equal_size and equal_alphas and equal_content

directory = 'test_images_decrypt'
os.system("Remove-item alias:curl") # execute this line to prevent windows from running their version of curl
os.system("""curl -F "file=@test_images.zip" http://127.0.0.1:5000/upload -H "username: patel" -H "password: 4120" """)
# curl -F 'file=@test_images.zip' http://127.0.0.1:5000/upload -H "username: patel" -H "password: 4120"

 
# iterate over files in original image directory comparing each to the result from the API call
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    os.system(f'curl -o {filename} http://127.0.0.1:5000/retrieve -H \"username: patel\" -H \"password: 4120\" -H \"img_name: {filename}\"')
    img = Image.open(filename)
    img_real = Image.open(f'{directory}/{filename}')
    result = are_images_equal(img, img_real)
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("The curl command did not generate an output file")
    if (result):
        print("All tests succeeded and files are accurate")
    else:
        print(filename, "was not correctly decrypted/encrypted")
    
    # curl -o shopify.png http://127.0.0.1:5000/retrieve -H "username: patel" -H "password: 4120" -H "img_name: shopify.png"