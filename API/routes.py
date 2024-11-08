import logging
from Database.Models import ini_db, Base, User, Setup, Image, Score
from fastapi import FastAPI,APIRouter, Depends, HTTPException, File, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import get_password_hash, verify_password
import datamodels as dm
from datetime import datetime, timedelta, timezone
import shutil
router = APIRouter()

#log config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#JWT config

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = "mysql+pymysql://user:user@localhost/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(user_name: str, password: str):
    logger.info(f'Authenticating user {user_name}')
    user = get_user(user_name)
    if not user:
        logger.warning(f'User {user_name} not found')
        return False
    if not verify_password(password, user.password_hash):
        logger.warning(f'Invalid password for user {user_name}')
        return False
    logger.info(f'User {user_name} authenticated successfully')
    return user


def get_user(user_name: str | None):
    with Session(engine) as session:
        return session.query(User).filter(User.username == user_name).first()

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

ini_db(DATABASE_URL)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=dm.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logging.info(f'Logging in user {form_data.username}')
    user = authenticate_user(form_data.username, form_data.password)
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
    logging.info(f'User {form_data.username} logged in successfully')
    return {"access_token": access_token, "token_type": "bearer"}

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

@app.post("/setups/", response_model=dm.Setup)
async def create_setup(setup : dm.Setup, db: Session = Depends(get_db)):
    setup = Setup(user_id=setup.user_id, gear=setup.gear, ammo=setup.ammo, position=setup.position, drills=setup.drills)
    db.add(setup)
    db.commit()
    db.refresh(setup)
    return setup

@app.get("/setups/{user_id}/")
async def get_setups(user_id: int, db: Session = Depends(get_db)):
    setups = db.query(Setup).filter(Setup.user_id == user_id).all()
    return setups

@app.post("/upload/")
async def upload_image( user_id: int, setup_id: int, file: UploadFile = File(...),db: Session = Depends(get_db)):
    # logger.info("bonjour")    
    file_path = f"API/images/{file.filename}"
    with open(file_path, "wb") as image_file:
       logger.info(f"Saving image to {file_path}")
        
       shutil.copyfileobj(file.file, image_file)


        #image_file.write(await file.read())
    image = Image(user_id=user_id, setup_id=setup_id, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

@app.get("/users/{user_id}/images/")
async def get_user_images(user_id: int, db: Session = Depends(get_db)):
    images = db.query(Image).filter(Image.user_id == user_id).all()
    return images

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port =8000)
