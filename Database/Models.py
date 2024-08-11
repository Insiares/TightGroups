
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = relationship("Image", back_populates="owner")
    setups = relationship("Setup", back_populates="owner")

class Setup(Base):
    __tablename__ = "setups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gear = Column(String(255))
    ammo = Column(String(255))
    position = Column(String(255))
    drills = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="setups")
    images = relationship("Image", back_populates="setup")

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    setup_id = Column(Integer, ForeignKey("setups.id"), nullable=True)
    file_path = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="images")
    setup = relationship("Setup", back_populates="images")
    scores = relationship("Score", back_populates="image")

class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    score_value = Column(Float)
    group_size = Column(Float)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    
    image = relationship("Image", back_populates="scores")

Base.metadata.create_all(bind=engine)
