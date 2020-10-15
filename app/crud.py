from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.orm import Session

from . import ALGORITHM
from . import models
from . import schemas
from . import SECRET_KEY
from .utils import get_db
from .utils import get_password_hash
from .utils import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_db_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_db_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_db_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_db_user(db: Session, user: schemas.UserCreate):
    dict_user = user.dict(exclude={"password"})
    dict_user["hashed_password"] = get_password_hash(user.password)
    db_user = models.User(**dict_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
