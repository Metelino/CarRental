from typing import Optional, List
from functools import partial
import datetime

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# import crud
# import models
# import schemas
import crud, models, schemas, auth
from database import SessionLocal, engine
from auth import verify_role, verify_user

#admin_role = lambda : verify_role(roles=['admin'])
admin_role = partial(verify_role, roles=['admin'])

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/users/register", response_model=schemas.Token, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db=db, user=user) 
        return auth.create_jwt(id=db_user.id, role=db_user.role)
    except:
        raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/users", status_code=204)
def edit_user(user: schemas.UserEdit, user_id: int = Depends(auth.verify_user), db: Session = Depends(get_db)):
    if crud.update_user(db, user):
        return Response(status_code=204)
    raise HTTPException(status_code=404, detail="User doesn't exist")

@app.delete("/users/{user_id}", status_code=204, dependencies=[Depends(admin_role)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if crud.delete_user(db, user_id):
        return Response(status_code=204)
    raise HTTPException(status_code=404, detail="User doesn't exist")

@app.delete("/users", status_code=204)
def delete_user(user_id: int = Depends(verify_user), db: Session = Depends(get_db)):
    if crud.delete_user(db, user_id):
        return Response(status_code=204)
    raise HTTPException(status_code=404, detail="User doesn't exist")

@app.post("/users/login", response_model=schemas.Token, status_code=200)
def login(user: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user is not None:
        if db_user.password == user.password:
            return auth.create_jwt(id=db_user.id, role=db_user.role)
    raise HTTPException(401, detail='Invalid email or password')

@app.get("/users", response_model=List[schemas.User], status_code=200, dependencies=[Depends(admin_role)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

@app.post("/cars", response_model=schemas.Car, dependencies=[Depends(admin_role)])
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    return crud.create_car(db, car)

@app.delete("/cars/{car_id}", dependencies=[Depends(admin_role)], status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    crud.delete_car(db, car_id)
    return Response(status_code=204)

@app.patch("/cars", dependencies=[Depends(admin_role)], status_code=204)
def edit_car(car: schemas.CarEdit, db: Session = Depends(get_db)):
    if crud.update_car(db, car):
        return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Car doesn't exist")
    
@app.get("/cars", response_model=List[schemas.Car])
def read_cars(offset: int, db: Session = Depends(get_db)):
    db_cars = crud.get_cars(db, offset*10, 10)
    return db_cars

@app.get("/cars/{car_id}", response_model=schemas.Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car doesn't exist")
    return db_car

@app.get("/rentals/car/{car_id}", response_model=List[schemas.Rental], status_code=200)
def car_active_rentals(car_id: int, db: Session = Depends(get_db)):
    if crud.check_car(db, car_id):
        return crud.get_active_rentals_by_car(db, car_id)
    raise HTTPException(status_code=404, detail="Car doesn't exist")

@app.get("/rentals", response_model=List[schemas.Rental], status_code=200)
def user_active_rentals(user_id: int = Depends(auth.verify_user), db: Session = Depends(get_db)):
    if crud.check_user(db, user_id):
        return crud.get_active_rentals_by_user(db, user_id)
    raise HTTPException(status_code=404, detail="User doesn't exist")


@app.get("/rentals/unpaid", response_model=List[schemas.Rental], status_code=200)
def user_unpaid_rentals(user_id: int = Depends(auth.verify_user), db: Session = Depends(get_db)):
    if crud.check_user(db, user_id):
        return crud.get_unpaid_rentals_by_user(db, user_id)
    raise HTTPException(status_code=404, detail="User doesn't exist")

@app.get("/rentals/pay/{rental_id}", status_code=204)
def pay_rental(rental_id: int, user_id: int = Depends(auth.verify_user), db: Session = Depends(get_db)):
    if crud.check_user(db, user_id):
        rental = crud.get_rental(db, rental_id)
        if rental.user_id == user_id:
            crud.rental_pay(db, rental_id)
            return Response(status_code=204)
        raise HTTPException(403, "Not user's rental")
    raise HTTPException(status_code=404, detail="User doesn't exist")

@app.get("/rentals/user/{user_id}", dependencies=[Depends(admin_role)], response_model=List[schemas.Rental], status_code=200)
def user_all_rentals(user_id: int, db: Session = Depends(get_db)):
    if crud.check_user(db, user_id):
        return crud.get_all_rentals_by_user(db, user_id)
    raise HTTPException(status_code=404, detail="User doesn't exist")

@app.post("/rentals", response_model=schemas.Rental, status_code=201)
def create_rental(rental: schemas.RentalCreate, user_id: int = Depends(auth.verify_user), db: Session = Depends(get_db)):
    if crud.check_car(db, rental.car_id):
        db_rental = crud.create_rental(db, user_id, rental)
        if db_rental:
            return db_rental
        raise HTTPException(status_code=400, detail="Car is already rented for the chosen period of time")
    raise HTTPException(status_code=404, detail="Car doesn't exist")

@app.patch("/rentals", status_code=204, dependencies=[Depends(admin_role)])
def change_rental(rental: schemas.RentalDateEdit, db: Session = Depends(get_db)):
    if crud.check_rental(db, rental.id):
        crud.update_rental(db, rental)
        return Response(status_code=204)
    raise HTTPException(404, "Rental does not exist")

# @app.patch("/rentals", status_code=204)
# def change_rental(rental: schemas.RentalDateEdit, user_id: int = Depends(verify_user), db: Session = Depends(get_db)):
#     db_rental = crud.get_rental(db, rental.id)
#     if db_rental is not None:
#         if db_rental.user_id == user_id:
#             crud.update_rental(db, rental)
#             return Response(status_code=204)
#     raise HTTPException(400, "Given rental does not exist")

@app.patch("/rentals/{rental_id}", status_code=204)
def stop_rental(rental_id: int, user_id: int = Depends(verify_user), db: Session = Depends(get_db)):
    db_rental = crud.get_rental(db, rental_id)
    if db_rental is not None:
        if db_rental.user_id == user_id:
            if crud.stop_rental(db, rental_id):
                return Response(status_code=204)
            #raise HTTPException(205, "Given rental hasn't started yet")
            Response(status_code=205)
    raise HTTPException(404, "Given rental does not exist")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
