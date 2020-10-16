from typing import Dict
from typing import List

from pydantic import BaseModel
from pydantic import Field


class UserBase(BaseModel):
    email: str = Field(..., example="johndoe@gmail.com")
    username: str = Field(..., example="john37")
    full_name: str = Field(..., example="John Doe")


class UserCreate(UserBase):
    password: str = Field(..., example="Secret^123$")


class User(UserBase):
    id: int
    disabled: bool = Field(..., example=False)

    class Config:
        orm_mode = True


class SurveyBase(BaseModel):
    title: str
    description: str


class SurveyCreate(SurveyBase):
    questions: List[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "Programmer Survey",
                "description": "Annual Programmer survey",
                "questions": [
                    "Do you like Object-Oriented Programming?",
                    "Are you proficient in Java?",
                ]
            }
        }


class Survey(SurveyBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class TakeSurvey(BaseModel):
    questions: Dict[str, bool]

    class Config:
        schema_extra = {
            "example": {
                "questions": {
                    "Do you like Object-Oriented Programming?": True,
                    "Are you proficient in Java?": False,
                }
            }
        }


class UserResponse(BaseModel):
    username: str
    response: Dict[str, bool]

    class Config:
        schema_extra = {
            "example": {
                "username": "john37",
                "response": {
                    "Do you like Object-Oriented Programming?": True,
                    "Are you proficient in Java?": False,
                },
            }
        }


class SurveyStats(BaseModel):
    total: int = 0
    agree: int = 0
    percentage: float = 0


class SurveyResult(SurveyBase):
    responses: List[UserResponse]
    stats: Dict[str, SurveyStats]

    class Config:
        schema_extra = {
            "example": {
                "title": "Programmer Survey",
                "description": "Annual Programmer survey",
                "responses": [
                    {
                        "username": "john37",
                        "response": {
                            "Do you like Object-Oriented Programming?": True,
                            "Are you proficient in Java?": False
                        }
                    }
                ],
                "stats": {
                    "Do you like Object-Oriented Programming?": {
                        "total": 1,
                        "agree": 1,
                        "percentage": 100
                    },
                    "Are you proficient in Java?": {
                        "total": 1,
                        "agree": 0,
                        "percentage": 0
                    }
                }
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str
