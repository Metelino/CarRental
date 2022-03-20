from email.policy import default
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import SessionLocal
#from sqlalchemy_utils.types import ChoiceType

Base = declarative_base()

class User(Base):
    # TYPES = [
    #     (u'admin', u'Admin'),
    #     (u'regular_user', u'Regular user')
    # ]
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True, default='regular_user')
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
    car_id = Column(Integer, ForeignKey(Car.id, ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    rental_start = Column(Date, index=True)
    rental_end = Column(Date, index=True)

    #car = relationship("Car", back_populates="rentals")
    #user = relationship("User", back_populates="rentals")

if __name__ == "__main__":
    admin_user = User(role='admin', name='Wojciech', surname='Metelski', email='dasfasf@gmail.com', password='admin123')
    with SessionLocal() as db:
        db.add(admin_user)
        db.commit()