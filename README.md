# Car Rental Backend

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)

<!-- * [License](#license) -->

## General Information

Backend application for purposes of renting cars. 
Application exposes REST API for use for frontend apps. 

## Technologies Used

- Python - version 3.9.7
- Uvicorn - version 0.17.6
- FastAPI - version 0.75.0
- SQLAlchemy - version 1.4.32

## Features

- user validation and authorization using JWT
- create account, rent cars for a chosen period of time (user)
- add new cars, edit existing rentals (admin)

## Setup
To run  you need python installed. All project dependencies are listed in requirements.txt.
To install all deps run:\
`pip install -r requirements.txt`\
To run app start a uvicorn server pointing to FastAPI instance:\
`uvicorn main:app -- reload`
