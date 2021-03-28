
from ..config.db import database

async def initializeUser(id):
    users_query = "INSERT INTO users (user_id, user_state_id) VALUES (:user_id, :user_state_id)"
    users_values = {"user_id" : id, "user_state_id" : 1}
    await database.execute(query=users_query, values=users_values)

    users_space_config = "INSERT INTO user_space_configurations (user_id) VALUES (:user_id)"
    space_config_values = {"user_id" : id}
    await database.execute(query=users_space_config, values=space_config_values)

    folders_query = "INSERT INTO folders (name, created_by_user, parent_directory_id, folder_state_id, \
        folder_scope_id) VALUES (:name, :created_by_user, :parent_directory_id, :folder_state_id, \
        :folder_scope_id)"
    folders_values = {"name" : "root", "created_by_user": id, 
                "parent_directory_id": None, "folder_state_id" : 1, "folder_scope_id" : 1 }
    await database.execute(query=folders_query, values=folders_values)





