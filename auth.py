from datetime import datetime, timedelta
from typing import Optional, List

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt(expires_delta: Optional[timedelta] = None, **kwargs):
    payload = dict(**kwargs)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    jwtoken = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {'token':jwtoken}

security = HTTPBearer()

def verify_token(creds = Depends(security)):
    token = creds.credentials
    #print(token)
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    expired_exception = HTTPException(
        status_code=403,
        detail="Token is expired",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload['exp']
        #print(exp)
        #print(datetime.utcfromtimestamp(exp))
        #print(datetime.utcnow())
        if exp is None:
            raise credentials_exception
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise expired_exception
        return payload
    except JWTError:
        raise credentials_exception

def verify_user(payload = Depends(verify_token)):
    return int(payload['id'])

def verify_role(roles, payload = Depends(verify_token)):
    #print("PRZED AUTH")
    if payload['role'] not in roles:
        raise HTTPException(
            status_code=401,
            detail="You don't have privileges",
        )
    #print("PO AUTH")
