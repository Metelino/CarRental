from typing import Optional, List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# import crud
# import models
# import schemas
import crud, models, schemas, auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "Siema Eniu"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # db_user = crud.get_user_by_email(db, email=user.email)
    # if db_user:
    try:
        return crud.create_user(db=db, user=user) 
    except:
        raise HTTPException(status_code=400, detail="Email already registered")
    

@app.post("/users/login", response_model=schemas.Token, status_code=200)
def login(user: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user is not None:
        if db_user.password == user.password:
            return auth.create_jwt(db_user.id)
    raise HTTPException(401, detail='Invalid email or password')

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/cars", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = crud.create_car(db, car)
    return db_car

@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    pass

@app.put("/cars/{car_id}")
def edit_car(car: schemas.Car, db: Session = Depends(get_db)):
    pass
    
@app.get("/cars", response_model=List[schemas.Car])
def read_cars(offset: int, db: Session = Depends(get_db)):
    db_cars = crud.get_cars(db, offset*10, 10)
    return db_cars

@app.get("/rentals/car/{car_id}", response_model=List[schemas.Rental], status_code=200)
def car_rentals(car_id: int, db: Session = Depends(get_db)):
    if crud.get_car(db, car_id) is not None:
        return crud.get_rentals_by_car(db, car_id)
    raise HTTPException(status_code=400, detail="Car doesn't exist")

@app.get("/rentals/user/{user_id}", response_model=List[schemas.Rental], status_code=200)
def user_rentals(user_id: int, db: Session = Depends(get_db)):
    if crud.get_user(db, user_id) is not None:
        return crud.get_rentals_by_user(db, user_id)
    raise HTTPException(status_code=400, detail="User doesn't exist")

@app.post("/rentals/", response_model=schemas.Rental, status_code=201)
def create_rental(rental: schemas.RentalCreate, user_id: int = Depends(auth.verify_jwt), db: Session = Depends(get_db)):
    db_rental = crud.create_rental(db, user_id, rental)
    if db_rental:
        return db_rental
    raise HTTPException(status_code=400, detail="Car is already rented for the chosen period of time")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)