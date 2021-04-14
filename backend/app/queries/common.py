from ..config.db import database


async def get_object_scope_id(scope):
    query = "SELECT id FROM object_scopes WHERE scope_type = :scope"
    result = await database.fetch_one(query=query, values={"scope": scope})
    return result


async def get_object_state_id(state):
    query = "SELECT id FROM object_states WHERE state_type = :state"
    result = await database.fetch_one(query=query, values={"state": state})
    return result


async def get_user_state_id(state):
    query = "SELECT id FROM user_states WHERE user_state_type = :state"
    result = await database.fetch_one(query=query, values={"state": state})
    return result
