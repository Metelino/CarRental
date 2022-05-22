from typing import List, Optional, Union
from datetime import date

from pydantic import BaseModel, validator, EmailStr

class CarCreate(BaseModel):
    brand: str
    model: str
    description: str 
    img: str
    price: str

class CarEdit(BaseModel):
    brand: Optional[str] = ""
    model: Optional[str] = ""
    description: Optional[str] = "" 
    img: Optional[str] = ""
    price: Optional[str] = ""

class Car(CarCreate):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr

class UserIn(UserBase):
    password: str

class UserCreate(UserBase):
    name: str
    surname: str
    password: str

class UserEdit(BaseModel):
    email: Optional[str] = ""
    name: Optional[str] = ""
    surname: Optional[str] = ""
    password: Optional[str] = ""

class User(UserBase):
    id: int
    name: str
    surname: str
    active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    token: str

class RentalBase(BaseModel):
    rental_start: Optional[date] = ""
    rental_end: Optional[date] = ""

    @validator('rental_end')
    def valid_date_range(cls, v, values, **kwargs):
        if 'rental_start' in values and v < values['rental_start']:
            raise ValueError('Invalid date range')
        return v

    @validator('rental_start', 'rental_end')
    def not_expired_date(cls, v, values, **kwargs):
        TODAY = date.today()
        if v < TODAY:
            raise ValueError("Expired date") 
        return v

# class RentalDateEdit(RentalBase):
#     id: int
    
class RentalCreate(RentalBase):
    car_id: int

class Rental(RentalBase):
    car: Car
    #car_id: int
    user_id: int
    id: int
    total_price : float

    class Config:
        orm_mode = True
