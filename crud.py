import base64
import imghdr
import pathlib
import datetime
import os
from django.http import Http404

from sqlalchemy.orm import Session
from fastapi import HTTPException

import models, schemas

BASE_DIR = pathlib.Path(__file__).resolve().parent

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(404, "User doesn't exist")
    return user

def check_user(db: Session, user_id: int):
    return db.query(models.User.id).filter(
        models.User.id == user_id,
    ).first() is not None

def get_user_by_email(db: Session, email: str):
    user = db.query(models.User).filter(
        models.User.email == email,
        models.User.active == True
    ).first()
    if user is None:
        raise HTTPException(404, "User doesn't exist")
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    #fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserEdit):
    db_user = get_user(db, user_id)
    for attr, value in user.dict(exclude_defaults=True).items():
        setattr(db_user, attr, value)
    db.commit()

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    db_user.active = False
    db.commit()

def get_car(db: Session, car_id: int):
    car = db.query(models.Car).filter_by(id=car_id).first()
    if car is None:
        raise HTTPException(404, "Car doesn't exist!")
    return car

def check_car(db: Session, car_id: int):
    return db.query(models.Car.id).filter(
        models.Car.id == car_id, 
        models.Car.active == True
    ).first() is not None

def get_cars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Car).filter(models.Car.active == True).offset(skip).limit(limit).all()

def decode_image(img_str):
    try:
        img_bytes = base64.b64decode(img_str)
        ext = imghdr.what(None, h=img_bytes)
        return (img_bytes, ext)
    except:
        raise HTTPException(400, "Invalid image format!")

def save_img(path, file_bytes):
    print(BASE_DIR / path)
    with open(BASE_DIR / path, 'wb') as file_to_save:
        file_to_save.write(file_bytes)

def delete_img(path):
    try:
        os.remove(BASE_DIR / path)
    except:
        pass

def create_car(db: Session, car: schemas.CarCreate):
    # Obraz auta jest w base64, po odkodowaniu i zapisaniu pliku
    # w bazie danych zostaje zapisana ścieżka do pliku
    img_bytes, ext = decode_image(car.img)
    db_car = models.Car(**car.dict())
    db_car.img = ""
    db.add(db_car)
    db.flush()
    db.refresh(db_car)
    img_path = f'media/cars/car_{db_car.id}.{ext}'
    save_img(img_path, img_bytes)
    db_car.img = img_path
    db.flush()
    #db.refresh(db_car)
    db.commit()
    return db_car

def update_car(db: Session, car_id: int, car: schemas.CarEdit):
    db_car = get_car(db, car_id)
    img_path = None
    if car.img != "":
        img_bytes, ext = decode_image(car.img)
        img_path = f'media/cars/car_{db_car.id}.{ext}'
        delete_img(car.img)
        #save_img(db_car.img, img_bytes)
        save_img(img_path, img_bytes)
        db_car.img = img_path
    for attr, value in car.dict(exclude_defaults=True).items():
        setattr(db_car, attr, value)
    if img_path:
        setattr(db_car, 'img', img_path)
    db.commit()

def delete_car(db: Session, car_id : int):
    db_car = get_car(db, car_id)
    db_car.active = False
    db.commit()
        
def get_active_rentals_by_car(db: Session, car_id: int):
    TODAY = datetime.date.today()
    rentals = db.query(models.Car).filter(models.Car.id == car_id).first().rentals
    return rentals.filter(models.Rental.rental_end >= TODAY).all()

def get_active_rentals_by_user(db: Session, user_id: int):
    TODAY = datetime.date.today()
    rentals = db.query(models.User).filter(models.User.id == user_id).first().rentals
    return rentals.filter(models.Rental.rental_end >= TODAY).all()

def get_all_rentals_by_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first().rentals.all()

def get_unpaid_rentals_by_user(db: Session, user_id: int):
    rentals = db.query(models.User).filter(models.User.id == user_id).first().rentals
    return rentals.filter(models.Rental.paid == False).all()

def get_rental(db: Session, rental_id: int):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if rental is None:
        raise HTTPException(404, "Rental doesn't exist")
    return rental

def rental_pay(db: Session, rental_id: int):
    rental = get_rental(db, rental_id)
    rental.paid = True
    db.commit()

def check_rental(db: Session, rental_id: int):
    return db.query(models.Rental.id).filter(models.Rental.id == rental_id).first() is not None

def check_rental_active(db: Session, rental_id):
    TODAY = datetime.date.today()
    rental = db.query(models.Rental.id).filter(models.Rental.id == rental_id).first()
    return rental.rental_end >= TODAY

def create_rental(db: Session, user_id: int, rental: schemas.RentalCreate):
    db_rentals = get_active_rentals_by_car(db, rental.car_id)
    start = rental.rental_start
    end = rental.rental_end

    #DAY = datetime.timedelta(days=1)
    for r in db_rentals: # Sprawdzanie czy okres wynajmu nie nachodzi na inny wynajem
        if (start >= r.rental_start and start <= r.rental_end) or \
        (end >= r.rental_start and end <= r.rental_end) or \
        (start < r.rental_start and end > r.rental_end):
            raise HTTPException(409, "Car is taken for given period!")

    db_item = models.Rental(**rental.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_rental(db: Session, rental_id: int, rental: schemas.RentalBase):
    current_rental = get_rental(db, rental_id)
    if current_rental.paid:
        raise HTTPException(409, "Rental has been paid for the whole period!")
    db_rentals = get_active_rentals_by_car(db, current_rental.car_id)
    #db_rentals = db_rentals.filter(models.Rental.id != rental.id).all()
    start = rental.rental_start
    end = rental.rental_end

    #DAY = datetime.timedelta(days=1)
    for r in db_rentals: # Sprawdzanie czy okres wynajmu nie nachodzi na inny wynajem
        if r.id == current_rental.id:
            continue
        if (start >= r.rental_start and start <= r.rental_end) or \
        (end >= r.rental_start and end <= r.rental_end) or \
        (start < r.rental_start and end > r.rental_end):
            raise HTTPException(409, "Car is taken for given period!")

    for attr, value in rental.dict(exclude_defaults=True).items():
        setattr(current_rental, attr, value)
    db.commit()

def stop_rental(db: Session, rental_id: int):
    db_rental = get_rental(db, rental_id)
    TODAY = datetime.date.today()
    DAY = datetime.timedelta(days=1)
    if db_rental.paid:
        raise HTTPException(409, "Rental has been paid for the whole period!")
    if db_rental.rental_start > TODAY:
        db.delete(db_rental)
        db.commit()
        return
    db_rental.rental_end = TODAY + DAY
    db.commit()

# def delete_rental(db: Session, rental_id: int):
#     db_rental = get_rental(db, rental_id)
#     if db_rental is not None:
#         db.delete(db_rental)
#         db.commit()
#         return True
#     return False