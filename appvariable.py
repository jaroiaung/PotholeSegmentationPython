import os
from io import BytesIO
from flask import Flask, render_template, request, send_file
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,Text
from sqlalchemy.orm import relationship, sessionmaker


UPLOAD_FOLDER = 'static/uploads/'
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

engine = create_engine("mysql+mysqlconnector://root:e/jBj9WKf2242EbSobpznoh+M19Jf18rjxJm+ujIip8=@srv-cmgcjm021fec739pfv4g-5b6bdb88f5-t58jt:3306/mysql", echo=True)

Base = declarative_base()

class PotholeOrignal(Base):
    __tablename__= 'pothole_orignal'
    __table_args__ = {'schema': 'mysql'}
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    filepath = Column(Text)
    address = Column(Text)

    def __repr__(self):
        return f"<id: {self.id}, filename: {self.filename}, filepath: {self.filepath}, address: {self.address} >"

class PotholeScanned(Base):
    __tablename__= 'pothole_scanned'
    __table_args__ = {'schema': 'mysql'}
    id = Column(Integer, primary_key=True)
    filename = Column(Text)
    filepath = Column(Text)
    address = Column(Text)
    parent_id = Column(Integer, ForeignKey('mysql.pothole_orignal.id'))
    pothole = relationship('PotholeOrignal')

    def __repr__(self):
        return f"<id: {self.id}, filename: {self.filename}, filepath: {self.filepath}, address: {self.address}, parent_id: {self.parent_id} >"

Base.metadata.create_all(engine)
sessionmaker = sessionmaker()
sessionmaker.configure(bind= engine)
sessionDb = sessionmaker()



