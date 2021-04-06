from ..config.db import database


async def exists(folder_name, user_id):
    query = "SELECT * FROM folders WHERE name = :name AND created_by_user = :id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name": folder_name})
    return result


async def move(folder, parent_directory):
    query = "UPDATE folders SET parent_directory_id = :parent_id WHERE id = :folder_id RETURNING id"
    values = {"parent_id": parent_directory, "folder_id": folder}
    return await database.execute(query=query, values=values)


async def insert_folder(folder, user_id, parent_dir_id, scope_id):
    query = "INSERT INTO folders (name, created_by_user, parent_directory_id, folder_state_id, \
        folder_scope_id) VALUES (:name, :created_by_user, :parent_directory_id, :folder_state_id, \
        :folder_scope_id)"
    values = {"name": folder, "created_by_user": user_id,
              "parent_directory_id": parent_dir_id, "folder_state_id": 1, "folder_scope_id": scope_id}
    await database.execute(query=query, values=values)
