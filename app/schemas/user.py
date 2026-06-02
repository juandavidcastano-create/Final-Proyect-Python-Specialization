from typing import Optional

from pydantic import BaseModel, EmailStr

class userlogin(BaseModel):
    email: EmailStr
    password: str

#to-do - pasar la validación de data a schemas, para que el servicio solo se encargue de la lógica de
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    repeated_password: str
    def validate_passwords(self):
        if self.password != self.repeated_password:
            raise ValueError("Passwords do not match")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
