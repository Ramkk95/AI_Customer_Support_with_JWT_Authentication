from datetime import datetime,timedelta, timezone
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
SECRET_KEY = 'KHARBOOJA'
ALGORITHM='HS256'
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')

def create_token(data:dict):
    to_encode= data.copy()
    expire= datetime.now(timezone.utc)+timedelta(minutes=30)
    to_encode.update({'exp':expire})
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

def creat_new_user(token :str= Depends(oauth2_scheme)):
    try:
        payload= jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username= payload.get('sub')
        if username is None:
            raise HTTPException(status_code=400,detail='Invalid username')
        return username

    except JWTError:
        raise HTTPException(status_code=400,detail='Invalid username or password')

