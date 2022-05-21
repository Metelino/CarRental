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
    brand: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None 
    img: Optional[str] = None
    price: Optional[str] = None

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

class UserEdit(UserBase):
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    name: str
    surname: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    token: str

class RentalBase(BaseModel):
    rental_start: Optional[date] = None
    rental_end: Optional[date] = None

    @validator('rental_end')
    def valid_date_range(cls, v, values, **kwargs):
        if 'rental_start' in values and v < values['rental_start']:
            raise ValueError('Invalid date range')
        return v

    @validator('*')
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
    car_id: int
    user_id: int
    id: int
    total_price : float

    class Config:
        orm_mode = True
