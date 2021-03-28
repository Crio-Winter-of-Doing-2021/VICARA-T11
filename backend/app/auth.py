from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from .config.db import UserDB, user_db
from .models.user import User, UserCreate, UserUpdate
SECRET = "305cafbd0092e367476d9239aa27fcd7d623591fa65b4ae2026936040f45f36a"
jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=3600, tokenUrl="/auth/jwt/login"
)


fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)