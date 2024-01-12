import os
from io import BytesIO
from flask import Flask, render_template, request, send_file
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,Text
from sqlalchemy.orm import relationship, sessionmaker


UPLOAD_FOLDER = 'static/uploads/'
#UPLOAD_FOLDER = '/home/jaroi1991/mysite/static/uploads/'
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

engine = create_engine("mysql+mysqlconnector://root:mapunG26@localhost:3306/flaskDatabase", echo=True)

Base = declarative_base()

class PotholeOrignal(Base):
    __tablename__= 'pothole_orignal'
    __table_args__ = {'schema': 'flaskDatabase'}
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    filepath = Column(Text)
    address = Column(Text)

    def __repr__(self):
        return f"<id: {self.id}, filename: {self.filename}, filepath: {self.filepath}, address: {self.address} >"

class PotholeScanned(Base):
    __tablename__= 'pothole_scanned'
    __table_args__ = {'schema': 'flaskDatabase'}
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    filepath = Column(Text)
    address = Column(Text)
    parent_id = Column(Integer, ForeignKey('flaskDatabase.pothole_orignal.id'))
    pothole = relationship('PotholeOrignal')

    def __repr__(self):
        return f"<id: {self.id}, filename: {self.filename}, filepath: {self.filepath}, address: {self.address}, parent_id: {self.parent_id} >"

Base.metadata.create_all(engine)
sessionmaker = sessionmaker()
sessionmaker.configure(bind= engine)
sessionDb = sessionmaker()



