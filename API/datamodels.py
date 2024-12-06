from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)

class User(UserBase):
    id : Optional[int] = None
    model_config = ConfigDict(from_attributes=True
                              )

class Setup(BaseModel):
    id : Optional[int] = None
    user_id: int
    gear: str
    ammo: int | str
    position: str
    drills: str
    model_config = ConfigDict(from_attributes=True
                              )

class Ammo(BaseModel):
    id : Optional[int] = None
    name: str
    manufacturer: Optional[str] = None
    caliber: Optional[str] = None
    weight: Optional[float]= None
    weight_unit: Optional[str]= None
    V_0: Optional[float]= None
    V_0_unit: Optional[str]= None
    CB1: Optional[float]= None
    CB2: Optional[float]= None
    model_config = ConfigDict(from_attributes=True
                              )

class Seance(BaseModel):
    id : Optional[int] = None
    user_id: int
    # created_at: date
    temp_C: float
    wind_speed: float
    wind_gust: float
    wind_dir: float
    pressure: float
    precipitation: float

    model_config = ConfigDict(from_attributes=True
                              )

class Image(BaseModel):
    id : Optional[int] = None
    setup_id: int
    seance_id: int
    file_path: Optional[str]
   #  output_path: Optional[str]
    upload_date: Optional[date]
    model_config = ConfigDict(from_attributes=True
                              )
class Score(BaseModel):
    id : Optional[int] = None
    image_id: int
    score_value: float
    group_size: float
    output_path: str
    calculation_date: date
    model_config = ConfigDict(from_attributes=True
                              )

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
