from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi.middleware.cors import CORSMiddleware
from .queries.register import initializeUser
from .auth import fastapi_users, jwt_authentication
from .config.db import (database, engine, metadata, UserDB)
from .routers import files, folders
from .config.config import SECRET
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
    fastapi_users.get_auth_router(jwt_authentication),
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
app.include_router(folders.router, prefix="/folders", tags=["folders"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
