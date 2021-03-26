from fastapi import FastAPI

from .config.db import database, engine, metadata

metadata.create_all(engine)
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

