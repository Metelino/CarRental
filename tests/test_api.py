from fastapi.testclient import TestClient
import pytest
import base64
from pathlib import Path

from main import app
from auth import create_jwt

client = TestClient(app)

def test_default():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "Siema Eniu"}

def test_login():
    response = client.post(
        '/users/login',
        json={'email':'metel@gmail.com', 'password':'admin123'}
    )
    assert response.status_code == 200

    token = create_jwt(id=4, role='admin')
    assert response.json() == token

@pytest.fixture
def new_user():
    response = client.post(
        '/users/register',
        json={
            'name':'Wojciech', 
            'surname':'Metelski', 
            'email':'testowy_mail@gmail.com', 
            'password':'haslo'
        }
    )
    assert response.status_code == 200
    return response.json()['id']

@pytest.fixture
def edited_user(new_user):
    token = create_jwt(id=4, role='admin')['token']
    response = client.patch(
        f'/users/{new_user}',
        json={"email":"testowy_mail@gmail.com"},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 204
    return new_user

def test_user_delete(edited_user):
    token = create_jwt(id=4, role='admin')
    response = client.delete(
        f'/users/{edited_user}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 204

car_rental = {
    "rental_start": "2031-5-11",
    "rental_end": "2031-5-21",
    "car_id": 1
}

@pytest.fixture
def new_user_rental():
    token = create_jwt(id=2)['token']
    response = client.post(
        '/rentals',
        json=car_rental,
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    return response.json()['id']
    
@pytest.fixture
def checked_rental(new_user_rental):
    token = create_jwt(id=2)['token']
    response = client.get(
        '/rentals',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200

    def check_if_present():
        for r in response.json():
            if new_user_rental == r['id']:
                return True
        return False

    assert check_if_present()
    return new_user_rental

def test_delete_rental(checked_rental):
    token = create_jwt(id=2)['token']
    response = client.delete(
        f'/rentals/{checked_rental}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 204

def base64_encode():
    BASE_DIR = Path(__file__).resolve().parent
    with open(f"{BASE_DIR}/auto.jpg", "rb") as img:
        img_bytes = img.read()
        return base64.b64encode(img_bytes)

@pytest.fixture
def new_car():
    token = create_jwt(id=4, role='admin')['token']
    response = client.post(
        '/cars',
        json={
            "img":base64_encode(),
            "brand":"Skoda",
            "model":"Testowa",
            "description":"Testowe auto",
            "price":2137

        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    BASE_DIR = Path(__file__).resolve().parent.parent
    new_car = response.json()
    assert (BASE_DIR / f'media/{new_car["img"]}').is_file()
    return new_car['id']

@pytest.fixture
def updated_car(new_car):
    token = create_jwt(id=4, role='admin')['token']
    response = client.patch(
        f'/cars/{new_car}',
        json={
            #"img":base64_encode(),
            "brand":"Skoda",
            "model":"Testowa",
            "description":"Testowe auto",
            "price":2137
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 204
    return new_car

def test_delete_car(updated_car):
    token = create_jwt(id=2)['token']
    response = client.delete(
        f'/cars/{updated_car}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 204