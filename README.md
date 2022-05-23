# shopify-fall-2022-data-engineering
https://docs.google.com/document/d/1ijXrqQMOORukOWCWcwwcpxPcF_TczwvNE0wB4M2Orqg/edit#

# Encrypted Image Repository With Parallelization

## How it works?
 The repository is wrapped by a flask REST API service which runs a thread pool executor that can concurrently encrypt a huge amount of (large or small) photos extremely fast! The encryption is pretty simple and just mean to be a small addition to the project since I am currently learning about cryptography. Images are encrypted using XOR encryption combined with an offset to ensure that if an image is stolen a bad-actor can't just decrypt the image with the password.

 The thread pool executor runs on 8 threads but can be set to more if computational power increases. The image below is basically how a thread pool executor works. Each task is an instruction to first read the image file in binary format and then encrypt it using the encryption method
 <img src="https://www.baeldung.com/wp-content/uploads/2016/08/2016-08-10_10-16-52-1024x572.png" data-canonical-src="https://www.baeldung.com/wp-content/uploads/2016/08/2016-08-10_10-16-52-1024x572.png" width="700" height="500" />

## Features
- Upload a zip file of any number of images
- Secure storage of images by user
- Images encrypted in database so if the storage is hacked your images are not exposed
- Easy retrieval of images using REST API system 
- Runs on Flask and service can be hosted on a server

## Usage

### To upload run 
    - `curl -F "file=@{path to zipfile}" http://127.0.0.1:5000/upload -H "username: {username}" -H "password: {password}"`

    
### To retrieve images run
-  `curl -o {filename} http://127.0.0.1:5000/retrieve -H "username: patel" -H "password: 4120" -H "img_name: {filename}"`
- For the current items in the database (for testing) the username:password combos are `{patel:4120}` and `{shrey:230}`

### To run testing suite
    - run the `test_encryption.py` script

