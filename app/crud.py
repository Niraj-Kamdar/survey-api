from collections import defaultdict

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


async def get_current_user(db: Session = Depends(get_db),
                           token: str = Depends(oauth2_scheme)):
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
        current_user: models.User = Depends(get_current_user), ):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_db_user(db: Session, username: str):
    return db.query(
        models.User).filter(models.User.username == username).first()


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


def create_db_survey(db: Session, current_user: models.User,
                     survey: schemas.SurveyCreate):
    dict_survey = survey.dict(exclude={"questions"})
    dict_survey["owner_id"] = current_user.id
    db_survey = models.Survey(**dict_survey)
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    for question in survey.questions:
        db_question = models.Question(question=question,
                                      survey_id=db_survey.id)
        db.add(db_question)
        db.commit()
    return db_survey


def create_db_response(db: Session, current_user: models.User, survey_id: int,
                       survey: schemas.TakeSurvey):
    db_survey = db.query(
        models.Survey).filter(models.Survey.id == survey_id).first()

    if not db_survey:
        raise HTTPException(status_code=404, detail="Invalid survey_id")

    questions = (db.query(
        models.Question).filter(models.Question.survey_id == survey_id).all())
    answers = survey.questions
    for question in questions:
        db_response = (db.query(models.Response).filter(
            models.Response.user_id == current_user.id,
            models.Response.question_id == question.id,
        ).first())
        if db_response:
            new_answer = answers.get(question.question)
            db_response.answer = new_answer if new_answer is not None else db_response.answer
        elif answers.get(question.question) is not None:
            db_response = models.Response(
                answer=answers.get(question.question),
                question_id=question.id,
                user_id=current_user.id,
            )
            db.add(db_response)
        db.commit()


def get_survey_result(db: Session, survey_id: int):
    db_survey = db.query(
        models.Survey).filter(models.Survey.id == survey_id).first()

    if not db_survey:
        raise HTTPException(status_code=404, detail="Invalid survey_id")

    questions = (db.query(models.Question).join(
        models.Question.responses).filter(
            models.Question.survey_id == survey_id).all())
    result = defaultdict(dict)
    stats = defaultdict(schemas.SurveyStats)
    for question in questions:
        for response in question.responses:
            stats[question.question].total += 1
            stats[question.question].agree += response.answer
            result[response.user.username][question.question] = response.answer
        stats[question.question].percentage = round((
            stats[question.question].agree /
            stats[question.question].total) * 100, 2)
    responses = [
        schemas.UserResponse(username=username, response=response)
        for username, response in result.items()
    ]

    return schemas.SurveyResult(
        title=db_survey.title,
        description=db_survey.description,
        stats=stats,
        responses=responses,
    )
