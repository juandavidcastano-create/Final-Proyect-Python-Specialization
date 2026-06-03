from datetime import timedelta, datetime, timezone
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.db.database import get_db
from app.repository.user import UserRepository

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: dict) -> str:
	to_encode = data.copy()
	expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


def decode_access_token(token: str) -> dict:
	"""Decode and validate a JWT access token. Raises `JWTError` on failure."""
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		return payload
	except JWTError:
		raise


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
	try:
		payload = decode_access_token(token)
		user_id = payload.get("user_id")
		if user_id is None:
			raise JWTError()
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token",
			headers={"WWW-Authenticate": "Bearer"},
		)

	user = UserRepository(db).get_user_by_id(user_id)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="User not found",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return user

