from fastapi import FastAPI, Request
from fastapi.params import Depends

from .queries.register import initializeUser
from .auth import fastapi_users, jwt_authentication
from .config.db import (database, engine, metadata, UserDB)
from .routers import files

SECRET = "305cafbd0092e367476d9239aa27fcd7d623591fa65b4ae2026936040f45f36a"
metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


async def on_after_register(user: UserDB, request: Request):
    await initializeUser(user.id)
    print(f"User {user.id} has registered.")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


def after_verification_request(user: UserDB, token: str, request: Request):
    print(f"Verification requested for user {user.id}. \
        Verification token: {token}")



app.include_router(
    fastapi_users.get_auth_router(jwt_authentication,
                                  requires_verification=True),
    prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(on_after_register),
    prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(
        SECRET, after_forgot_password=on_after_forgot_password
    ),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(
        SECRET, after_verification_request=after_verification_request
    ),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users", tags=["users"]
)

app.include_router(files.router, prefix="/files", tags=["files"])

@app.get("/")
async def read_main(user=Depends(fastapi_users.get_current_active_user)):
    return {"msg": f"{user.email}" }

