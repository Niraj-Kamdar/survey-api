import os

SECRET_KEY = (
    os.getenv("SECRET_KEY")
    or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
ACCESS_TOKEN_EXPIRE_MINUTES = (int(ACCESS_TOKEN_EXPIRE_MINUTES)
                               if ACCESS_TOKEN_EXPIRE_MINUTES else 30)
APP_PATH = os.path.dirname(os.path.abspath(__file__))
