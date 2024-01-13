import os
from appvariable import app, sessionDb,PotholeOrignal,PotholeScanned
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, session, send_file, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
from ultralytics import YOLO
import uuid


@app.route('/')
def upload_form():
       
    return render_template('upload.html')

@app.route('/camera')
def showCamera():
    return render_template('media.html')

@app.route('/viewvideo')
def viewvideo():
    fullAddressToPass = getaddress(session['scannedpothole'])

    return render_template('view_video.html', id = session['scannedpothole'],address= fullAddressToPass)

@app.route('/process', methods=['POST']) 
def process(): 
    files = request.files
    fullAddress = request.form['address']
    file = files.get('file')
    videofilename = str(uuid.uuid4()) +".webm"
    with open(os.path.join(app.config['UPLOAD_FOLDER'], videofilename), 'wb') as f:
        video_stream = file.read()
        f.write(video_stream)
        
    videoPath = os.path.join(app.config['UPLOAD_FOLDER'], videofilename)
    try:
        potholeFile = PotholeOrignal(filename=videofilename, filepath=videoPath, address = fullAddress)
        sessionDb.add(potholeFile)
    except:
        sessionDb.rollback()
        raise
    else:
        sessionDb.commit()
        original_id = potholeFile.id
        sessionDb.close()

    session['id'] = original_id
    session['filename'] = videofilename

    model = YOLO("best.pt")
    results= model.predict(source=videoPath, save=True, conf=0.5)
    session['save_path'] = os.path.join(results[0].save_dir, videofilename)

    try:
        potholeFileScanned = PotholeScanned(filename= videofilename, filepath= session['save_path'],parent_id = session['id'], address = fullAddress)
        sessionDb.add(potholeFileScanned)
    except:      
        sessionDb.rollback()
        raise
    else:
        sessionDb.commit()
        scanned_id = potholeFileScanned.id
        sessionDb.close()

    response = jsonify(scanned_id)
    session['scannedpothole'] = scanned_id
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        pathName = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            potholeFile = PotholeOrignal(filename=file.filename, filepath=pathName, address = "")
            sessionDb.add(potholeFile)
        except:      
            sessionDb.rollback()
            raise
        else:
            sessionDb.commit()
            original_id = potholeFile.id
            sessionDb.close()
       
        session['id'] = original_id
        session['filename'] = filename
        model = YOLO("best.pt")
        results= model.predict(source=pathName, save=True, conf=0.5)
        if filename.lower().endswith(('.mp4')):
            filename = filename.replace('.mp4', '.avi')
        session['save_path'] = os.path.join(results[0].save_dir, filename)

        try:
            potholeFileScanned = PotholeScanned(filename= filename, filepath= session['save_path'],parent_id = session['id'], address = "")
            sessionDb.add(potholeFileScanned)
        except:      
            sessionDb.rollback()
            raise
        else:
            sessionDb.commit()
            scanned_id = potholeFileScanned.id
            sessionDb.close()

        flash('File is successfully uploaded.')
        return render_template('upload.html', id=scanned_id)

# create download function for download files
@app.route('/download/<upload_id>')
def download(upload_id):

    try:
        potholeScannedFile = sessionDb.query(PotholeScanned).filter_by(id=upload_id).first()
    except:      
        sessionDb.rollback()
        raise
    else:
        sessionDb.close()
   
    filePathVideo = potholeScannedFile.filepath
    fileNameVideo = potholeScannedFile.filename

    if filePathVideo.lower().endswith(('.webm')):
        filePathVideo = filePathVideo.replace('.webm', '.mp4')

    if filePathVideo.lower().endswith(('.avi')):
        filePathVideo = filePathVideo.replace('.avi', '.mp4')

    if fileNameVideo.lower().endswith(('.webm')):
        fileNameVideo = fileNameVideo.replace('.webm', '.mp4')

    if fileNameVideo.lower().endswith(('.avi')):
        fileNameVideo = fileNameVideo.replace('.avi', '.mp4')

    return send_file(os.path.join(filePathVideo),download_name=fileNameVideo, as_attachment=True)

@app.route('/getaddress/<upload_id>')
def getaddress(upload_id):
    try:
        potholeScannedFile = sessionDb.query(PotholeScanned).filter_by(id=upload_id).first()
    except:      
        sessionDb.rollback()
        raise
    else:
        address = potholeScannedFile.address
        sessionDb.close()
        
    return address


if __name__ == "__main__":
    app.run()