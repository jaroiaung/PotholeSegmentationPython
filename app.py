import os
from appvariable import app, sessionDb,PotholeOrignal,PotholeScanned
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, session, send_file, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
from ultralytics import YOLO
import uuid
from datetime import datetime
import pandas as pd

@app.route('/showresults/')
def showresults():

    table  = ''
    table += '<table class="table hoverTable">'
    table += '    <thead>'
    table += '        <tr>'
    table += '            <th>View</th>'
    table += '            <th>ID</th>'
    table += '            <th>File Name</th>'
    table += '            <th>File Path</th>'
    table += '            <th>Address</th>'
    table += '            <th>Created Date</th>'
    table += '        </tr>'
    table += '    </thead>'
    table += '    <tbody>'
    
    for item in sessionDb.query(PotholeScanned).all():
        ts = item.created_date.strftime("%m/%d/%Y, %H:%M:%S")

        table += '<tr data-id="' + str( item.id   ) + '" >'
        table += '<td><a href="/viewfiles/'+ str( item.id   )+'" >View</a></td>'
        table += '<td data-name="id">' + str( item.id   )  + '</td>'
        table += '<td data-name="filename">' + item.filename + '</td>'
        table += '<td data-name="filepath">' + item.filepath + '</td>'
        table += '<td data-name="address">' + item.address + '</td>'
        table += '<td data-name="created_date">' + ts + '</td>'
        table += '</tr>'

    table += '    </tbody>'
    table += '</table>' 
    
    return render_template( 'showresults.html', segment='datatables', table=table )

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

@app.route('/viewfiles/<upload_id>')
def viewfiles(upload_id):

    try:
        potholeScannedFile = sessionDb.query(PotholeScanned).filter_by(id=upload_id).first()
        id = potholeScannedFile.id
        filename= potholeScannedFile.filename
        address = potholeScannedFile.address
        filetype = ''
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filetype = 'image'
        else:
            filetype = 'video'
        
    except:      
        sessionDb.rollback()
        sessionDb.close()
        raise
    else:
        sessionDb.close()
   
    return render_template('view_file.html', id = id, filename=filename, address = address, filetype = filetype)

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
        potholeFile = PotholeOrignal(filename=videofilename, filepath=videoPath, address = fullAddress, created_date = datetime.now())
        sessionDb.add(potholeFile)
    except:
        sessionDb.rollback()
        sessionDb.close()
        raise
    else:
        sessionDb.commit()
        original_id = potholeFile.id
        sessionDb.close()

    session['id'] = original_id
    session['filename'] = videofilename

    model = YOLO(os.path.join(app.config['HOME_DIR'], 'best.pt'))
    results= model.predict(source=videoPath, save=True, conf=0.5)
    session['save_path'] = os.path.join(results[0].save_dir, videofilename)

    try:
        potholeFileScanned = PotholeScanned(filename= videofilename, filepath= session['save_path'],parent_id = session['id'], address = fullAddress, created_date = datetime.now())
        sessionDb.add(potholeFileScanned)
    except:      
        sessionDb.rollback()
        sessionDb.close()
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
            potholeFile = PotholeOrignal(filename=file.filename, filepath=pathName, address = "", created_date = datetime.now())
            sessionDb.add(potholeFile)
        except:      
            sessionDb.rollback()
            sessionDb.close()
            raise
        else:
            sessionDb.commit()
            original_id = potholeFile.id
            sessionDb.close()
       
        session['id'] = original_id
        session['filename'] = filename
        model = YOLO(os.path.join(app.config['HOME_DIR'], 'best.pt'))
        results= model.predict(source=pathName, save=True, conf=0.5)
        if filename.lower().endswith(('.mp4')):
            filename = filename.replace('.mp4', '.avi')
        session['save_path'] = os.path.join(results[0].save_dir, filename)

        try:
            potholeFileScanned = PotholeScanned(filename= filename, filepath= session['save_path'],parent_id = session['id'], address = "", created_date = datetime.now())
            sessionDb.add(potholeFileScanned)
        except:      
            sessionDb.rollback()
            sessionDb.close()
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
        sessionDb.close()
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

    return send_file(os.path.join(app.config['HOME_FILE_DIR'],filePathVideo),download_name=fileNameVideo, as_attachment=True)

@app.route('/getaddress/<upload_id>')
def getaddress(upload_id):
    try:
        potholeScannedFile = sessionDb.query(PotholeScanned).filter_by(id=upload_id).first()
    except:      
        sessionDb.rollback()
        sessionDb.close()
        raise
    else:
        address = potholeScannedFile.address
        sessionDb.close()
        
    return address


if __name__ == "__main__":
    app.run(port=5000)