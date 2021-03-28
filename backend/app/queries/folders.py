from ..config.db import database

async def exists(folder_name, user_id): 
    query = "SELECT id FROM folders WHERE name = :name AND created_by_user = :id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name" : folder_name})
    return result
