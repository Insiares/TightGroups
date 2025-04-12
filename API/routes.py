from API.Database.Models import ini_db, User, Setup, Image, Score, Ammo, Seance
from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    status,
    Form,
    Body,
)
import scipy.stats as stats
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from API.auth import get_password_hash, verify_password
import API.datamodels as dm
from datetime import datetime, timedelta, timezone
import shutil
import os
from loguru import logger
from API.ml.YOLO_inference import predict_groupsize
from API.ammo.ammo_treatment import treat_ammo_data
import pandas as pd
import sys
import glob
import dotenv
import numpy as np
import json

dotenv.load_dotenv()
# log config

logger.add("./asf_mount_point/app_storage/logs/routes_logs.log")
logger.add(sys.stdout)
# JWT config

SECRET_KEY = os.getenv("JWT_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
# Dict to store valid refresh token for testing, best practice seems to store in debug
refresh_tokens_dict: dict[str, str] = {}

# Same thing for blacklist
token_blacklist: set[str] = set()
refresh_token_blacklsit: set[str] = set()
# DATABASE_URL = "mysql+pymysql://user:user@localhost/mydb"
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

app = FastAPI(
    title="TightGroups API",
    description="API for TightGroups",
    version="0.0.1",
    openapi_url="/tightgroups_api/getdocs/openapi.json",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ini_db(DATABASE_URL)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@logger.catch()
def merge_ammo_data(db):
    stats = { "created" : 0,
              "updated" : 0 }
    df = treat_ammo_data()

    for _, row in df.iterrows():
        data_dict = row.to_dict()

        #does it exists?
        existing_item = db.query(Ammo).filter(Ammo.name == data_dict["name"]).first()
        if existing_item:
            for key, value in data_dict.items():
                if hasattr(existing_item, key) and value not in [None, np.nan, 'N/A', 'null', 'Null']:
                    setattr(existing_item, key, value)
            stats["updated"] += 1
        else:
            new_item = Ammo(**data_dict)
            db.add(new_item)
            stats["created"] += 1
    db.commit()

    return stats

@app.on_event("startup")
def start_up_ammo_merge():
    db = next(get_db())
    try :
        stats = merge_ammo_data(db)
        logger.info(f"Created {stats['created']} ammo and updated {stats['updated']} ammo on startup")
    except Exception as e:
        logger.error(f"Error while merging ammo data: {e}")

def authenticate_user(user_name: str, password: str) -> User:
    """
    Function to validate authentification of user
    """
    logger.info(f"Authenticating user {user_name}")
    user = get_user(user_name)
    if not user:
        logger.warning(f"User {user_name} not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.password_hash):
        logger.warning(f"Invalid password for user {user_name}")
        raise HTTPException(status_code=401, detail="Invalid Credentials ")
    logger.info(f"User {user_name} authenticated successfully")
    return user


def get_user(user_name: str | None):
    # query = select(User).filter(User.username == user_name)
    # logger.debug(type(db))
    with Session(engine) as db:
        user = db.query(User).filter(User.username == user_name).first()
    return user


# this function takes place of verify_token when called as a dependency
# @logger.catch()
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    """
    Dependency to validate token validity and extract user_id from token's sub

    args : encoded token (str)

    returns : decoded token (dict)
    """
    if token in token_blacklist:
        logger.error("Token is blacklisted")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            logger.error("Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token. Please log in again.",
            )
        return payload  # Token is valid, return decoded data
    except jwt.ExpiredSignatureError:  # token is expired
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired. Please refresh your token.",
        )
    except jwt.InvalidTokenError:  # token is Invalid
        logger.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Please log in again.",
        )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new access token for the user.

    Args:
        data (dict): The data to be included in the access token.
        expires_delta (timedelta, optional): The expiration time for the token.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # logger.debug(f'JWT Token created for {data}')
    return encoded_jwt


# @logger.catch()
def verify_token(
    token: str, secret: str
) -> dict:  # added secret key to args to test both tokens in the same function
    if token in token_blacklist or token in refresh_token_blacklsit:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted"
        )

    try:
        # logger.debug(f"token to verify: {token}")
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])

        # logger.info(f"verify_token : {payload}")
        logger.debug(f"Now : {datetime.now(tz=timezone.utc)}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/ammo/")
def get_ammo_list(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # return the list of ammo name
    ammo_list = [ammo.name for ammo in db.query(Ammo).all()] 
    return ammo_list


def check_ammo(existing_ammo: dm.Ammo, db: Session = Depends(get_db)):
    # logger.debug(f"Checking ammo {existing_ammo}, with name {existing_ammo.name}")
    searched_ammo = db.query(Ammo).filter(Ammo.name == existing_ammo.name).first()

    if searched_ammo:
        # logger.debug(f"Found existing ammo {searched_ammo.name}")
        return searched_ammo.id

    new_ammo = Ammo(name=str(existing_ammo.name))

    db.add(new_ammo)
    db.commit()
    db.refresh(new_ammo)
    new_ammo_id = db.query(Ammo).filter(Ammo.name == existing_ammo.name).first()

    # logger.debug(f"Created new ammo {new_ammo.name}")

    return new_ammo_id.id


@app.post("/token", response_model=dm.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password)
    logger.info(f"user logged : {user}")

    if not user:
        logger.warning(f"User {form_data.username} failed login")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    refresh_tokens_dict[str(user.id)] = refresh_token
    logger.info(f"User {form_data.username} logged in successfully")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "token_type": "bearer",
    }


# Here is the new route, should be called by the frontend (don't like it but eh)
# @logger.catch()
@app.post("/refresh", response_model=dm.Token)
def refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    if refresh_token in refresh_token_blacklsit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token is blacklisted"
        )
    payload = verify_token(refresh_token, REFRESH_SECRET_KEY)
    username = payload.get("sub")
    logger.debug(f"refresh token called for user {username}")
    logger.debug(refresh_tokens_dict)
    logger.debug(refresh_token)
    # Test the existance of the refresh token in our false DB (dict)
    if username is None or refresh_tokens_dict.get(username) != refresh_token:
        logger.debug(refresh_tokens_dict.get(username))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
       
    # new tokens
    new_access_token = create_access_token(data={"sub": str(username)})
    new_refresh_token = create_refresh_token(data={"sub": str(username)})

    # update dict
    refresh_tokens_dict[str(username)] = new_refresh_token
    logger.info(f"Tokens refreshed for user {username}")
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "user_id": username,
        "token_type": "bearer",
    }


# @app.get("/users/me")
# def read_users_me(current_user: dm.User = Depends(get_current_user)):
#     return current_user
@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), refresh_token: str = Body(...)):
    """Invalidate the access token to log out the user."""
    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token is already revoked."
        )
    if refresh_token in refresh_token_blacklsit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is already revoked.",
        )

    token_blacklist.add(token)
    refresh_token_blacklsit.add(refresh_token)
    # this will prevent any reuse of captured token
    return {"message": "Successfully logged out"}


@app.post("/users/", response_model=dm.User)
def create_user(user: dm.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user = User(email=user.email, username=user.username, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/seances/")
def create_seance(
    seance: dm.MeteoData, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        seance = Seance(
            user_id=user["sub"],
            temp_C=seance.temp_C,
            wind_speed=seance.wind_speed,
            wind_gust=seance.wind_gust,
            wind_dir=seance.wind_dir,
            pressure=seance.pressure,
            precipitation=seance.precipitation,
        )
        db.add(seance)
        db.commit()
        db.refresh(seance)
        # logger.info(f"Created seance {seance.id}")
        return seance
    except Exception as e:
        logger.error(f"Error creating seance: {e}")
        raise e


@app.get("/seances/")
def get_seances(user=Depends(get_current_user), db: Session = Depends(get_db)):
    seances = db.query(Seance).filter(Seance.user_id == user["sub"]).all()
    return seances


@app.post("/setups/", response_model=dm.Setup)
def create_setup(
    setup: dm.Setup, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        # logger.debug(f"current user : {user}")
        ammo_name = setup.ammo
        ammo_to_check = Ammo(name=ammo_name)
        ammo = check_ammo(ammo_to_check, db)
        # logger.debug(f"Ammo recieved : {ammo}")
        # logger.debug(f"Setup : {setup}")
        setup = Setup(
            user_id=user["sub"],
            name=setup.name,
            gear=setup.gear,
            ammo=ammo,
            position=setup.position,
            drills=setup.drills,
        )
        db.add(setup)
        db.commit()
        db.refresh(setup)
        # logger.info(f"Created setup {setup.id}")
        return setup

    except Exception as e:
        logger.error(f"Error creating setup: {e}")
        raise e


# @logger.catch()
@app.get("/setups/")
def get_setups(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # join ammo table to get ammo name
    # logger.debug(f"Getting setups for user {user}")
    setups = (
        db.query(Setup)
        .add_column(Ammo.name.label("ammo_name"))
        .join(Ammo, Setup.ammo == Ammo.id)
        .filter(Setup.user_id == user["sub"])
        .all()
    )

    # logger.debug(f"retrieve setup query : {[setup for setup in setups]}")
    # setups = db.query(Setup).filter(Setup.user_id == user_id).all()
    result = [
        {
            **setup[0].__dict__,  # Setup model attributes
            "ammo_name": setup[1],  # The additional column
        }
        for setup in setups
    ]
    return result


@app.get("/gears/")
def get_gears(user=Depends(get_current_user), db: Session = Depends(get_db)):
    gears = db.query(Setup).filter(Setup.user_id == user["sub"]).distinct(Setup.gear)
    return gears


@app.post("/upload/")
def upload_image(
    setup_id: int = Form(...),
    seance_id: int = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # file_path = f".//images/{file.filename}"
    file_path = os.path.join(
        "./asf_mount_point/app_storage", os.path.join("images", file.filename)
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as image_file:
        logger.info(f"Saving image to {file_path}")

        shutil.copyfileobj(file.file, image_file)

        # image_file.write(await file.read())
    image = Image(seance_id=seance_id, setup_id=setup_id, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@app.get("/users/images/")
def get_user_images(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # logger.debug(f"Getting images for user {user_id}")
    images = db.query(Image).join(Setup).filter(Setup.user_id == user["sub"]).all()
    return images


@app.get("/images/{image_id}/")
def get_image(
    image_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    logger.debug(f"Getting image {image_id}")
    image = db.query(Image).filter(Image.id == image_id).first()
    image_treadted_path = image.file_path.replace("images", "images_treated")

    return image_treadted_path


# @logger.catch
@app.post("/inference/")
def inference(
    seance_id: int = Form(...),
    image_id: int = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.debug(f"Inference for seance {seance_id}")
    image_path = db.query(Image).filter(Image.id == image_id).first().file_path
    # model_path = "./runs/detect/train16/weights/best.pt"
    model_path = "impact_detector_best.pt"
    # extract image name from image_path

    image_name = image_path.split("/")[-1]

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # logger.debug(f"Current directory: {current_dir}")
    # input_path = os.path.join(current_dir, os.path.join("images", image_name))
    # outputh_path = os.path.join(
    #     current_dir, os.path.join("images_treated", image_name)
    # )  # TODO : be less dumb than this

    outputh_path = os.path.join(
        "./asf_mount_point/app_storage", os.path.join("images_treated", image_name)
    ) # That seems less dumb, but still dumb
    logger.debug(
        f"called predict_groupsize with {model_path}, {image_path}, {outputh_path}"
    )
    results = predict_groupsize(image_path, model_path, outputh_path)
    logger.debug(f"model output : {results}")
    score = Score(
        image_id=image_id,
        group_size=results if results > 0 else 0,
        calculation_date=datetime.now(timezone.utc),
    )
    db.add(score)
    db.commit()
    db.refresh(score)

    return results


# test routes for uptime check
# @logger.catch
@app.post("/inference/test/")
def inference_test():
    model_path = "impact_detector_best.pt"
    # extract image name from image_path
    image_path = "./tests/static/test_photo.jpg"
    image_name = image_path.split("/")[-1]
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # input_path = os.path.join(current_dir, os.path.join("images", image_name))
    outputh_path = os.path.join(
        "./asf_mount_point/app_storage", os.path.join("images_treated", image_name)
    )  # TODO : be less dumb than this
    results = predict_groupsize(image_path, model_path, outputh_path)
    return results


@app.get("/scores/")
def get_scores(user=Depends(get_current_user), db: Session = Depends(get_db)):
    query_not_dumb = f"""

    SELECT scores.group_size
            ,setups.id 
            , setups.gear
            , ammo.name as ammo
            , ammo.caliber
            , ammo.weight
            , ammo.V_0
            , ammo.CB1
            , setups.name
            , setups.position
            , setups.drills
            , seances.temp_C
            , seances.wind_speed
            , seances.pressure
            , seances.precipitation
            , seances.created_at

    FROM scores
    JOIN images ON images.id = scores.image_id
    JOIN setups ON images.setup_id = setups.id
    JOIN ammo ON setups.ammo = ammo.id
    JOIN seances ON images.seance_id = seances.id
    WHERE setups.user_id = {user["sub"]}
    AND scores.group_size > 0
    """
    scores = pd.read_sql_query(query_not_dumb, db.bind, index_col=None)
    # logger.debug(f"Scores : {scores.describe()}")
    json_result = json.loads(scores.to_json(orient="records"))
    return json_result

@app.post("/detection_failure/")
def remove_fail(
    image_id = Form(...),
    user : int = Depends(get_current_user),
    db : Session = Depends(get_db) ):

    image = db.query(Image).filter(Image.id == image_id).first()
    score = db.query(Score).filter(Score.image_id == image_id).first()
    db.delete(score)
    db.delete(image)
    db.commit()
    logger.warning(f"Deleted failed detection on image {image_id}")
    return

@app.get("/health/")
def health():
    files = glob.glob("./asf_mount_point/app_storage/runs/detection_*/labels/*.txt")
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    last_50_files = files[:50]
    all_detections = []
    all_confidences = []
    min_detections_threshold = 5
    min_confidence_threshold = 0.45
    outlier_threshold = 3
    for file in last_50_files:
        with open(file, "r") as f:
            detections = 0
            lines = f.readlines()
            for line in lines:
                values = line.strip().split(" ")
                confidence = float(values[5])
                detections += 1
                all_confidences.append(confidence)

            all_detections.append(detections)

    if all_confidences:
        confidence_outliers = np.abs(stats.zscore(all_confidences)) > outlier_threshold

        if (
            np.mean(all_detections) < min_detections_threshold
            or np.any(all_detections == 0)
            or np.mean(all_confidences) < min_confidence_threshold
            or np.any(confidence_outliers)
        ):
            status = "unhealthy"
        else:
            status = "healthy"
    else:
        status = "unhealthy"

    return JSONResponse(content={"status": status}, media_type="application/json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
