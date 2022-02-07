from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY = openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_ttl

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(value: str):
    return pwd_context.hash(value)

def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data:dict):

    copy = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    copy.update({"exp": expire})
    encoded_jwt = jwt.encode(copy, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# run the logic of verifying the token - returns nothing but throws an error on wrong access token
def verify_access_token(token: str, cred_except):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if not id:
            raise cred_except

    except JWTError:
        raise cred_except
    
    return schemas.TokenData(id=id)

# provide for dependency to run the logic of the verify_access_token() function
def get_current_user(token: str = Depends(oauth2_scheme),  db: Session = Depends(database.get_db)):
    cred_except = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, cred_except)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user