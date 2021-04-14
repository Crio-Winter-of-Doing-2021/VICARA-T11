
from ..config.db import database
from ..queries import common


async def initializeUser(id):
    private_scope = await common.get_object_scope_id("private")
    private_scope_id = private_scope["id"]
    active_state = await common.get_object_state_id("active")
    active_state_id = active_state["id"]
    user_state = await common.get_user_state_id("activated")
    user_state_id = user_state["id"]

    users_query = "INSERT INTO users_info (user_id, user_state_id) VALUES (:user_id, :user_state_id)"
    users_values = {"user_id": id, "user_state_id": user_state_id}
    await database.execute(query=users_query, values=users_values)

    users_space_config = "INSERT INTO user_space_configurations (user_id) VALUES (:user_id)"
    space_config_values = {"user_id": id}
    await database.execute(query=users_space_config, values=space_config_values)

    root_query = "INSERT INTO folders (name, created_by_user, parent_directory_id, folder_state_id, \
        folder_scope_id, full_path) VALUES (:name, :created_by_user, :parent_directory_id, :folder_state_id, \
        :folder_scope_id, :full_path)"
    root_values = {"name": str(id) + "_root", "created_by_user": id,
                   "parent_directory_id": None, "folder_state_id": active_state_id,
                   "folder_scope_id": private_scope_id, "full_path": "/root"}
    await database.execute(query=root_query, values=root_values)

    # trash_query = "INSERT INTO folders (name, created_by_user, parent_directory_id, folder_state_id, \
    #     folder_scope_id) VALUES (:name, :created_by_user, :parent_directory_id, :folder_state_id, \
    #     :folder_scope_id)"
    # trash_values = {"name": str(id) + "_trash", "created_by_user": id,
    #                 "parent_directory_id": None, "folder_state_id": active_state_id, "folder_scope_id": public_scope_id}
    # await database.execute(query=trash_query, values=trash_values)
