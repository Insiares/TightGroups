from Database.Models import ini_db, Base, User, Setup, Image, Score
from fastapi import FastAPI,APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import get_password_hash, verify_password
import datamodels as dm
router = APIRouter()

DATABASE_URL = "mysql+pymysql://user:user@localhost/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()
ini_db(DATABASE_URL)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=dm.User)
def create_user(user : dm.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user = User(email=user.email, username=user.username, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/setups/", response_model=dm.Setup)
def create_setup(setup : dm.Setup, db: Session = Depends(get_db)):
    setup = Setup(user_id=setup.user_id, gear=setup.gear, ammo=setup.ammo, position=setup.position, drills=setup.drills)
    db.add(setup)
    db.commit()
    db.refresh(setup)
    return setup

@app.get("/setups/{user_id}/")
def get_setups(user_id: int, db: Session = Depends(get_db)):
    setups = db.query(Setup).filter(Setup.user_id == user_id).all()
    return setups

@app.post("/upload/")
async def upload_image( user_id: int, setup_id: int, file: UploadFile = File(...),db: Session = Depends(get_db)):
    file_path = f"images/{file.filename}"
    with open(file_path, "wb") as image_file:
        image_file.write(await file.read())
    image = Image(user_id=user_id, setup_id=setup_id, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

@app.get("/users/{user_id}/images/")
def get_user_images(user_id: int, db: Session = Depends(get_db)):
    images = db.query(Image).filter(Image.user_id == user_id).all()
    return images

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port =8000)
