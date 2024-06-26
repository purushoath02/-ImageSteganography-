from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile
from stegano import lsb
import os
import glob 


app = Flask(__name__)




app.config['UPLOAD_FOLDER'] = '/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# def clear_temp_directory(directory):
#     if os.path.exists(directory):
#         for root, dirs, files in os.walk(directory, topdown=False):
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 try:
#                     os.remove(file_path)
#                 except OSError as e:
#                     print(f"Error deleting {file_path}: {e}")
#             for dir_name in dirs:
    
#                 dir_path = os.path.join(root, dir_name)
#                 try:
#                     os.rmdir(dir_path)
#                 except OSError as e:
#                     print(f"Error deleting {dir_path}: {e}")
#         try:
#             print(f"Successfully cleared {directory}")
#         except OSError as e:
#             print(f"Error deleting {directory}: {e}")
#     else:
#         print(f"Directory {directory} does not exist.")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    files = glob.glob('/uploads/*')
    for file in files: 
        os.remove(file)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return 'No image uploaded'
    text = request.form['text']
    print(text)
    image = request.files['image']

    if image.filename == '':
        return 'No Image selected'

    if text and allowed_file(image.filename):
        image.save('uploads/' + image.filename)
        img_path = os.path.join('uploads/', image.filename)
        print(img_path)

        output_path = os.path.join('stego_' + secure_filename(image.filename))
        secret = lsb.hide(img_path, text)
        secret.save(output_path)
        try:
            return send_file(output_path, as_attachment=True)
        finally:
            print("Cleaning up")
            os.remove(img_path)
            os.remove(output_path)
            #clear_temp_directory(temp_dir)

    else:
        return 'File type not allowed'

@app.route('/decrypt/', methods=['POST'])
def decrypt():
    if 'd_image' not in request.files:
        return 'No file part'
    image = request.files['d_image']
    if allowed_file(image.filename):
        image.save('uploads/' + image.filename)
        img_path = os.path.join('uploads/', image.filename)
        #(img_path)

        try:
            secret = lsb.reveal(image)
            #print('secret is :' + secret)
            #return send_file(decrypted_path, as_attachment=True)
            return render_template('output.html', output_text = secret)
        finally:
            print("Cleaning up")
            os.remove(img_path)
            #os.remove(output_path)
            #clear_temp_directory(temp_dir)
        

if __name__ == '__main__':
    app.run(debug=True)
