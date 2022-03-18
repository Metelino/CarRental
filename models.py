from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    rentals = relationship("Rental")

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    img = Column(String, index=True) # ścieżka do pliku w media
    description = Column(String, index=True)
    
    rentals = relationship("Rental")

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey(Car.id))
    user_id = Column(Integer, ForeignKey(User.id))
    rental_start = Column(Date, index=True)
    rental_end = Column(Date, index=True)

    #car = relationship("Car", back_populates="rentals")
    #user = relationship("User", back_populates="rentals")