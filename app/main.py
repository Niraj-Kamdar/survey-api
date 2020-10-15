import re
from datetime import timedelta

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import ACCESS_TOKEN_EXPIRE_MINUTES
from . import crud
from . import models
from . import schemas
from .database import engine
from .utils import create_access_token
from .utils import get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
validate_email = re.compile(
    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/users/",
    response_model=schemas.User,
    responses={
        400: {
            "description": "Invalid request body!",
            "model": schemas.Message
        },
    },
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creates new user with the following information:
    - **username** - username of the user that will be used for login
    - **full_name** - full name of the user
    - **email**: email of the user
    - **password**: password of the user
    """
    if validate_email.fullmatch(user.email):
        db_user = crud.get_db_user(db, username=user.username)
        if db_user:
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"Username: {user.username} already registered"
                },
            )
        db_user = crud.create_db_user(db=db, user=user)
        return db_user
    return JSONResponse(
        status_code=400,
        content={"message": f"Email: {user.email} is invalid!"},
    )


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
        current_user: models.User = Depends(crud.get_current_active_user)):
    """
    Returns information of current user:
    - **username** - username of the user that will be used for login
    - **full_name** - full name of the user
    - **email**: email of the user
    """
    return current_user


@app.post("/surveys", response_model=schemas.Survey)
async def create_survey(
        survey: schemas.SurveyCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(crud.get_current_active_user),
):
    db_survey = crud.create_db_survey(db, current_user, survey)
    return db_survey


@app.put("/surveys/{survey_id}", response_model=schemas.Message)
async def take_survey(survey_id: int, survey: schemas.TakeSurvey, db: Session = Depends(get_db),
                      current_user: models.User = Depends(crud.get_current_active_user), ):
    crud.create_db_response(db, current_user, survey_id, survey)
    return {"message": "Your response has been registered successfully!"}


@app.get("/surveys/{survey_id}")  # , response_model=schemas.SurveyResult)
async def view_survey_result(
        survey_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(crud.get_current_active_user)
):
    return crud.get_survey_result(db, survey_id)
