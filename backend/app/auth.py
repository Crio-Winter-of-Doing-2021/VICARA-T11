from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from .config.db import UserDB, user_db
from .models.user import User, UserCreate, UserUpdate
from .config.config import SECRET

jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=604800, tokenUrl="/auth/jwt/login"
)


fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
