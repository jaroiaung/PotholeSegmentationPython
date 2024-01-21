import os
from io import BytesIO
from flask import Flask, render_template, request, send_file
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,Text,DateTime
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

UPLOAD_FOLDER = 'static/uploads/'
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "secret key"
app.config['HOME_DIR'] =''
app.config['HOME_FILE_DIR'] = ''
app.config['UPLOAD_FOLDER'] = app.config['HOME_DIR']+ UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


app.config['DB_User'] = 'root'
app.config['DB_Password'] = 'mapunG26'
app.config['DB_HOST'] = 'localhost'
app.config['DB_Port'] = '3306'
app.config['DB_Database'] = 'flaskDatabase'

engine = create_engine("mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}".format(app.config['DB_User'], app.config['DB_Password'], app.config['DB_HOST'], app.config['DB_Port'],app.config['DB_Database']), echo=True)

Base = declarative_base()

class PotholeOrignal(Base):
    __tablename__= 'pothole_orignal'
    __table_args__ = {'schema': app.config['DB_Database']}
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    filepath = Column(Text)
    address = Column(Text)
    created_date = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return f"<id: {self.id}, filename: {self.filename}, filepath: {self.filepath}, address: {self.address} >"

class PotholeScanned(Base):
    __tablename__= 'pothole_scanned'
    __table_args__ = {'schema': app.config['DB_Database']}
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    filepath = Column(Text)
    address = Column(Text)
    created_date = Column(DateTime, default=datetime.now())
    parent_id = Column(Integer, ForeignKey(app.config['DB_Database']+'.pothole_orignal.id'))
    pothole = relationship('PotholeOrignal')

    def __repr__(self):
        return f"<id: {self.id}, filename: {self.filename}, filepath: {self.filepath}, address: {self.address}, parent_id: {self.parent_id} >"

Base.metadata.create_all(engine)
sessionmaker = sessionmaker()
sessionmaker.configure(bind= engine)
sessionDb = sessionmaker()



