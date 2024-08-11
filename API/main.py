
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user = models.User(username=username, email=email, password_hash=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/setups/")
def create_setup(user_id: int, gear: str, ammo: str, position: str, drills: str, db: Session = Depends(get_db)):
    setup = models.Setup(user_id=user_id, gear=gear, ammo=ammo, position=position, drills=drills)
    db.add(setup)
    db.commit()
    db.refresh(setup)
    return setup

@app.get("/setups/{user_id}/")
def get_setups(user_id: int, db: Session = Depends(get_db)):
    setups = db.query(models.Setup).filter(models.Setup.user_id == user_id).all()
    return setups

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), user_id: int, setup_id: int, db: Session = Depends(get_db)):
    file_path = f"images/{file.filename}"
    with open(file_path, "wb") as image_file:
        image_file.write(await file.read())
    image = models.Image(user_id=user_id, setup_id=setup_id, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

@app.get("/users/{user_id}/images/")
def get_user_images(user_id: int, db: Session = Depends(get_db)):
    images = db.query(models.Image).filter(models.Image.user_id == user_id).all()
    return images
