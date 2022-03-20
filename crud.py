import base64
import imghdr
import pathlib

from sqlalchemy.orm import Session

import models, schemas

BASE_DIR = pathlib.Path(__file__).resolve().parent

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def check_user(db: Session, user_id: int):
    return db.query(models.User.id).filter(models.User.id == user_id) is not None

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    #fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: schemas.User):
    db_user = get_user(db, user.id)
    if db_user is not None:
        db_user.update(**user.dict())
        db.commit()
        return True
    return False

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is not None:
        db_user.delete()
        db.commit()
        return True
    return False

def get_car(db: Session, car_id: int):
    return db.query(models.Car).filter_by(id=car_id).first()

def get_cars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Car).offset(skip).limit(limit).all()

def decode_image(img_str):
    img_bytes = base64.b64decode(img_str)
    ext = imghdr.what(None, h=img_bytes)
    return (img_bytes, ext)

def save_img(path, file_bytes):
    print(BASE_DIR / path)
    with open(BASE_DIR / path, 'wb') as file_to_save:
        file_to_save.write(file_bytes)


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

def update_car(db: Session, car : schemas.Car):
    db_car = get_car(db, car.id)
    if db_car is not None:
        db_car.update(**car.dict())
        db.commit()
        return True
    return False

def delete_car(db: Session, car_id : int):
    db_car = get_car(db, car_id)
    if db_car is not None:
        db_car.delete()
        db.commit()
        return True
    return False

def get_rentals_by_car(db: Session, car_id: int):
    return db.query(models.Car).filter(models.Car.id == car_id).first().rentals

def get_rentals_by_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first().rentals

def create_rental(db: Session, user_id: int, rental: schemas.RentalCreate):
    db_rentals = get_rentals_by_car(db, rental.car_id)
    start = rental.rental_start
    end = rental.rental_end
    for r in db_rentals: # Sprawdzanie czy okres wynajmu nie nachodzi na inny wynajem
        if start >= r.rental_start and start <= r.rental_end:
            return 
        elif end >= r.rental_start and end <= r.rental_end:
            return
        elif start < r.rental_start and end > r.rental_end:
            return

    db_item = models.Rental(**rental.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_rental(db: Session, rental_id: int):
    return db.query(models.Rental).filter(models.Rental.id == rental_id).first()

def delete_rental(db: Session, rental_id: int):
    db.query(models.Rental).filter(models.Rental.id == rental_id).delete()
    db.commit()