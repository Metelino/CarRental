from typing import List, Optional
from datetime import date

from pydantic import BaseModel

class RentalCreate(BaseModel):
    car_id: int
    rental_start: date
    rental_end: date

class Rental(RentalCreate):
    user_id: int
    id: int

    class Config:
        orm_mode = True

class CarCreate(BaseModel):
    brand: str
    description: Optional[str] = None
    img: str

class Car(CarCreate):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserIn(UserBase):
    password: str

class UserCreate(UserBase):
    name: str
    surname: str
    password: str

class User(UserBase):
    id: int
    name: str
    surname: str

    class Config:
        orm_mode = True

class UserEdit(UserBase):
    name: str
    surname: str
    password: str

class Token(BaseModel):
    token: str