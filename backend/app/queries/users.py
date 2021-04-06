from ..config.db import database


async def get_user(email):
    query = "SELECT id FROM \"user\" WHERE email = :email"
    result = await database.fetch_one(query=query, values={"email": email})
    return result


async def update_storage_limit(email):
    query = "SELECT id FROM \"user\" WHERE email = :email"
    result = await database.fetch_one(query=query, values={"email": email})
    return result


async def get_current_space(user_id):
    query = "SELECT SUM(size_in_gb) FROM files WHERE uploaded_by = :id"
    result = await database.fetch_one(query=query, values={"id": user_id})
    return result
