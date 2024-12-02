
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timezone


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # images = relationship("Image", back_populates="owner")
    setups = relationship("Setup", back_populates="owner")
    seances = relationship("Seance", back_populates="user")

class Seance(Base):
    __tablename__ = "seances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # end_time = Column(DateTime, default=datetime.now(timezone.utc))   #Why not but TBD
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    temp_C = Column(Float)
    wind_speed = Column(Float)
    wind_gust = Column(Float)
    wind_dir = Column(Float)
    pressure = Column(Float)
    precipitation = Column(Float)
    
    user = relationship("User", back_populates="seances"
                        )
    images = relationship("Image", back_populates="seances")

class Setup(Base):
    __tablename__ = "setups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gear = Column(String(255))
    ammo = Column(Integer, ForeignKey("ammo.id"), nullable = True)
    position = Column(String(255))
    drills = Column(String(255))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    owner = relationship("User", back_populates="setups")
    images = relationship("Image", back_populates="setup")
    ammo_used = relationship("Ammo", back_populates="ammo_used")

class Ammo(Base):
    __tablename__ = "ammo"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    manufacturer = Column(String(255), unique = False, index = True, nullable = True)
    caliber = Column(String(255), unique = False, index = True, nullable = True)
    weight = Column(Float, unique = False, index = False, nullable = True)
    weight_unit = Column(String(255), unique = False, index = False, nullable = True)
    V_0 = Column(Float, unique = False, index = False, nullable = True)
    V_0_unit = Column(String(255), unique = False, index = False, nullable = True)
    CB1 = Column(Float, unique = False, index = False, nullable = True)
    CB2 = Column(Float, unique = False, index = False, nullable = True)

    ammo_used = relationship("Setup", back_populates="ammo_used")
    

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    setup_id = Column(Integer, ForeignKey("setups.id"), nullable=True)
    seance_id = Column(Integer, ForeignKey("seances.id"), nullable=True)
    file_path = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.now(timezone.utc))
    

    setup = relationship("Setup", back_populates="images")
    seances = relationship("Seance", back_populates="images")
    scores = relationship("Score", back_populates="image")

class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    score_value = Column(Float)
    group_size = Column(Float)
    calculation_date = Column(DateTime, default=datetime.now(timezone.utc))
    
    image = relationship("Image", back_populates="scores")

def ini_db(DATABASE_URL):
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
