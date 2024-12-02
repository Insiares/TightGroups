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
    ammo: str
    position: str
    drills: str
    model_config = ConfigDict(from_attributes=True
                              )

class Ammo(BaseModel):
    id : Optional[int] = None
    name: str
    manufacturer: str
    caliber: str
    weight: float
    weight_unit: str
    V_0: float
    V_0_unit: str
    CB1: float
    CB2: float
    model_config = ConfigDict(from_attributes=True
                              )
class Seance(BaseModel):
    id : Optional[int] = None
    user_id: int
    model_config = ConfigDict(from_attributes=True
                              )

class Image(BaseModel):
    id : Optional[int] = None
    user_id: int
    setup_id: int
    file_path: str
    upload_date: date
    model_config = ConfigDict(from_attributes=True
                              )
class Score(BaseModel):
    id : Optional[int] = None
    image_id: int
    score_value: float
    group_size: float
    calculation_date: date
    model_config = ConfigDict(from_attributes=True
                              )

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
