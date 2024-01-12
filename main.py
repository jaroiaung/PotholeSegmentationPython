from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,Text
from sqlalchemy.orm import relationship, sessionmaker

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
session = sessionmaker()

potholeFile = PotholeOrignal(filename="test.jpg", filepath="static/uploads/test.jpg", address = "208 Bukit Batok Street 21, Block 208 Block 208, Singapore 650208")
session.add(potholeFile)
session.commit()

potholeFileScanned = PotholeScanned(filename="test.jpg", filepath= "runs/segment/predict/test.jpg",parent_id = potholeFile.id, address = "208 Bukit Batok Street 21, Block 208 Block 208, Singapore 650208")
session.add(potholeFileScanned)
session.commit()

potholes = session.query(PotholeOrignal).all()

pothole = session.query(PotholeOrignal).filter_by(id=6).first()

print(pothole)
