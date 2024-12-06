from API.Database.Models import ini_db, Base, User, Setup, Image, Score, Ammo, Seance
from fastapi import FastAPI,APIRouter, Depends, HTTPException, File, UploadFile, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from API.auth import get_password_hash, verify_password
import API.datamodels as dm
from datetime import datetime, timedelta, timezone
import shutil
import os
router = APIRouter()
from loguru import logger
from typing import Annotated
from API.ml.YOLO_inference import predict_groupsize
import pandas as pd
#log config

logger.add("routes_logs.log")
#JWT config

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = "mysql+pymysql://user:user@localhost/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ini_db(DATABASE_URL)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(user_name: str, password: str):
    logger.info(f'Authenticating user {user_name}')
    user = get_user(user_name)
    if not user:
        logger.warning(f'User {user_name} not found')
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.password_hash):
        logger.warning(f'Invalid password for user {user_name}')
        raise HTTPException(status_code=401, detail="Invalid Credentials ")
    logger.info(f'User {user_name} authenticated successfully')
    return user


def get_user(user_name: str | None ):
    # query = select(User).filter(User.username == user_name)
    # logger.debug(type(db))
    with Session(engine) as db:
        user = db.query(User).filter(User.username == user_name).first()
    return user



async def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.info(f'Getting current user token')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            logger.warning(f'Token sub not found')
            raise credentials_exception
        token_data = dm.TokenData(username=username)
        logger.info(f'Token sub found: {username}')
    except Exception as e: # lazy, TODO : add jwt specific exceptions
        logger.error(f'Error decoding token: {e}')
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        logger.warning(f' User {token_data.username} not found after token validation')
        raise credentials_exception
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:   
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f'JWT Token created for {data}')
    return encoded_jwt




def check_ammo(existing_ammo : dm.Ammo , db : Session = Depends(get_db) ):
    logger.debug(f"Checking ammo {existing_ammo}, with name {existing_ammo.name}") 
    searched_ammo = db.query(Ammo).filter(Ammo.name == existing_ammo.name).first()

    if searched_ammo:
        logger.debug(f"Found existing ammo {searched_ammo.name}")
        return searched_ammo.id

    new_ammo = Ammo(name=str(existing_ammo.name))

    db.add(new_ammo)
    db.commit()
    db.refresh(new_ammo)
    new_ammo_id = db.query(Ammo).filter(Ammo.name == existing_ammo.name).first(
        )

    logger.debug(f"Created new ammo {new_ammo.name}")

    return new_ammo_id.id

@app.post("/token", response_model=dm.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f'logger in user {form_data.username}')
    user = authenticate_user(form_data.username, form_data.password)
    logger.info(f"user logged : {user}")
    logger.debug(f"user type : {type(user)}")
    logger.debug(f"user id : {user.id}")

    if not user:
        logger.warning(f'User {form_data.username} failed login')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f'User {form_data.username} logged in successfully')
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}

@app.get("/users/me")
async def read_users_me(current_user: dm.User = Depends(get_current_user)):
    return current_user

@app.post("/users/", response_model=dm.User)
async def create_user(user : dm.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user = User(email=user.email, username=user.username, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/seances/", response_model=dm.Seance)
async def create_seance(seance : dm.Seance, db: Session = Depends(get_db)):
    try:
        seance = Seance(user_id = seance.user_id, temp_C = seance.temp_C, wind_speed = seance.wind_speed, wind_gust = seance.wind_gust, wind_dir = seance.wind_dir, pressure = seance.pressure, precipitation = seance.precipitation)
        db.add(seance)
        db.commit()
        db.refresh(seance)
        logger.info(f"Created seance {seance.id}")
        return seance
    except Exception as e:
        logger.error(f'Error creating seance: {e}')
        raise e

@app.get("/seances/{user_id}/")
async def get_seances(user_id: int, db: Session = Depends(get_db)):
    seances = db.query(Seance).filter(Seance.user_id == user_id).all()
    return seances

@app.post("/setups/", response_model=dm.Setup)
async def create_setup(setup : dm.Setup, db: Session = Depends(get_db)):
    try :
        ammo_name = setup.ammo
        ammo_to_check = Ammo(name=ammo_name)
        ammo = check_ammo(ammo_to_check, db)
        logger.debug(f"Ammo recieved : {ammo}")
        logger.debug(f"Setup : {setup}")
        setup = Setup(user_id=setup.user_id, gear=setup.gear, ammo=ammo, position=setup.position, drills=setup.drills)
        db.add(setup)
        db.commit()
        db.refresh(setup)
        logger.info(f"Created setup {setup.id}")
        return setup

    except Exception as e:
        logger.error(f'Error creating setup: {e}')
        raise e


@app.get("/setups/{user_id}/")
async def get_setups(user_id: int, db: Session = Depends(get_db)):
    setups = db.query(Setup).filter(Setup.user_id == user_id).all()
    return setups

@app.get("/gears/{users_id}/")
async def get_gears(users_id: int, db: Session = Depends(get_db)):
    gears = db.query(Setup).filter(Setup.user_id == users_id).distinct(Setup.gear)
    return gears

@app.post("/upload/")
async def upload_image(setup_id: int = Form(...), seance_id: int = Form(...), file: UploadFile = File(...),db: Session = Depends(get_db)):
    # logger.info("bonjour") 
    logger.debug(f"uploading image")
    file_path = f"./API/images/{file.filename}"
    with open(file_path, "wb") as image_file:
       logger.info(f"Saving image to {file_path}")
        
       shutil.copyfileobj(file.file, image_file )


        #image_file.write(await file.read())
    image = Image(seance_id=seance_id, setup_id=setup_id, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)   
    return image

@app.get("/users/{user_id}/images/")
async def get_user_images(user_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Getting images for user {user_id}")
    images = db.query(Image).join(Setup).filter(Setup.user_id == user_id).all()
    return images

@logger.catch
@app.post("/inference/{seance_id}/{image_id}/")
async def inference(seance_id : int, image_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Inference for seance {seance_id}")
    image_path = db.query(Image).filter(Image.id == image_id).first().file_path
    model_path = "/home/insia/Documents/Projects/TightGroups/runs/detect/train16/weights/best.pt"
    #extract image name from image_path
    image_name = image_path.split("/")[-1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Current directory: {current_dir}")
    input_path = os.path.join(current_dir, os.path.join("images", image_name))
    outputh_path = os.path.join(current_dir, os.path.join("images_treated", image_name)) # TODO : be less dumb than this
    logger.debug(f"called predict_groupsize with {model_path}, {input_path}, {outputh_path}")
    results = predict_groupsize(input_path,model_path, outputh_path)
    logger.debug(f"model output : {results}")
    score = Score(image_id = image_id, 
                  group_size = results, 
                  calculation_date = datetime.now(timezone.utc))
    db.add(score)
    db.commit()
    db.refresh(score)

    return results

@app.get("/scores/{user_id}/")
async def get_scores(user_id: int, db: Session = Depends(get_db)):
    query = f'''
    SELECT setups.gear 
          , ammo.name
          , setups.position
          , setups.drills
          , seances.temp_C
          , seances.wind_speed
          , seances.pressure
          , seances.precipitation
          , seances.created_at
          , scores.group_size
    FROM setups
    JOIN ammo ON setups.ammo = ammo.id
    JOIN seances ON setups.user_id = seances.user_id
    JOIN images ON seances.id = images.seance_id
    JOIN scores ON images.id = scores.image_id
    WHERE setups.user_id = {user_id}
    '''                                                                              
    scores = pd.read_sql_query(query, db.bind, index_col = None)    
    return scores.to_dict("records")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port =8000)
