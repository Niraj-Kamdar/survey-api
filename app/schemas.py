from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(..., example="johndoe@gmail.com")
    username: str = Field(..., example="john37")
    full_name: str = Field(..., example="John Doe")


class UserCreate(UserBase):
    password: str = Field(..., example="Secret^123$")


class User(UserBase):
    id: int
    disabled: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str
