from pydantic import BaseModel, EmailStr, model_validator

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    repeated_password: str

    @model_validator(mode="after")
    def validate_passwords(cls, values):
        password = values.password
        repeated_password = values.repeated_password
        if password != repeated_password:
            raise ValueError("Passwords do not match")
        return values

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
