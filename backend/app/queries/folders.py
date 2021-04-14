from ..config.db import database
from ..queries import common, files
from datetime import datetime


async def find_by_name(folder_name, user_id):
    query = "SELECT * FROM folders WHERE name = :name AND created_by_user = :id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name": folder_name})
    return result


async def insert_folder(folder, parent_dir_id, state_id, scope_id, user_id):
    parent_full_path_data = await get_full_path(folder_id=parent_dir_id)
    full_path = parent_full_path_data["full_path"] + \
        "/" + folder
    query = "INSERT INTO folders (name, created_by_user, parent_directory_id, folder_state_id, \
        folder_scope_id, full_path) VALUES (:name, :created_by_user, :parent_directory_id, :folder_state_id, \
        :folder_scope_id, :full_path) RETURNING id"
    values = {"name": folder, "created_by_user": user_id,
              "parent_directory_id": parent_dir_id,
              "folder_state_id": state_id, "folder_scope_id": scope_id,
              "full_path": full_path}
    try:
        result = await database.execute(query=query, values=values)
        return result
    except:
        return -1


async def get_folder_data(folder_id, user_id, state_id):
    query = "SELECT folders.id, folders.name, folders.created_on, folders.full_path,\
        object_scopes.scope_type FROM folders \
        INNER JOIN object_scopes ON folders.folder_scope_id = object_scopes.id \
        WHERE created_by_user = :user_id AND folders.id = :folder_id AND folders.folder_state_id = :state_id"
    result = await database.fetch_one(query=query, values={"user_id": user_id, "folder_id": folder_id, "state_id": state_id})
    return result


async def get_full_path(folder_id):
    query = "SELECT * FROM folders WHERE id = :folder_id"
    result = await database.fetch_one(query=query, values={"folder_id": folder_id})
    return result


async def get_folders_in_parent(parent_directory_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT folders.id, folders.name, folders.created_on, folders.full_path,\
        object_scopes.scope_type FROM folders \
        INNER JOIN object_scopes ON folders.folder_scope_id = object_scopes.id \
        WHERE folders.parent_directory_id = :folder_id AND folders.folder_state_id = :state_id\
        ORDER BY folders.created_on DESC"
    result = await database.fetch_all(query=query, values={"folder_id": parent_directory_id, "state_id": active_state["id"]})
    return result


async def get_root_dir(user_id):
    query = "SELECT * FROM folders WHERE created_by_user = :user_id AND parent_directory_id IS NULL"
    result = await database.fetch_one(query=query, values={"user_id": user_id})
    return result


async def change_folder_scope(folder_id, scope_id):
    query = "UPDATE folders SET folder_scope_id = :scope_id WHERE id = :folder_id RETURNING id"
    result = await database.execute(query=query, values={"folder_id": folder_id, "scope_id": scope_id})
    return result


async def exists_and_active(folder_id, user_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT * FROM folders WHERE id = :folder_id AND created_by_user = :user_id AND folder_state_id = :state_id"
    result = await database.fetch_one(query=query, values={"user_id": user_id, "folder_id": folder_id, "state_id": active_state["id"]})
    return result


async def set_inactive(folder_id):
    query = "INSERT INTO folders_inactive (folder_id) VALUES (:folder_id) RETURNING id"
    values = {"folder_id": folder_id}
    try:
        await database.execute(query=query, values=values)
    except:
        return -1
    inactive_state = await common.get_object_state_id("inactive")
    query = "UPDATE folders SET folder_state_id = :state_id WHERE id = :folder_id RETURNING id"
    result = await database.execute(query=query, values={"folder_id": folder_id, "state_id": inactive_state["id"]})
    active_state = await common.get_object_state_id("active")
    query = "SELECT id FROM files WHERE parent_directory_id = :folder_id AND file_state_id = :state_id"
    file_list = await database.fetch_all(query=query, values={"folder_id": folder_id, "state_id": active_state["id"]})
    for file in file_list:
        await files.set_inactive(file_id=file["id"])
    return result


async def get_by_id(folder_id):
    query = "SELECT * FROM folders WHERE id = :folder_id"
    result = await database.fetch_one(query=query, values={"folder_id": folder_id})
    return result


async def parent_dir_active(folder_id):
    dir = await get_by_id(folder_id)
    if dir["parent_directory_id"] is None and dir["full_path"] == "/root":
        return 1
    parent_dir = await get_by_id(dir["parent_directory_id"])
    parent_dir_active = await exists_and_active(folder_id=parent_dir["id"], user_id=dir["created_by_user"])
    return parent_dir_active


async def move(folder_id, parent_dir_id):
    parent_dir_data = await get_full_path(folder_id=parent_dir_id)
    folder_data = await get_full_path(folder_id=folder_id)
    suggested_name = folder_data["name"]
    suggested_path = parent_dir_data["full_path"] + "/" + suggested_name
    user_id = folder_data["created_by_user"]
    constraint_violated = await folderpath_constraint(full_path=suggested_path, user_id=user_id)
    if constraint_violated:
        return -1
    result = await update_folder_parent_dir(folder_id=folder_id, folder_name=suggested_name, folder_path=suggested_path, parent_dir=parent_dir_id)
    await update_full_path_children(old_path_prepend=folder_data["full_path"], new_path_prepend=suggested_path, user_id=user_id)
    return result


async def folderpath_constraint(full_path, user_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT * FROM folders WHERE created_by_user = :user_id AND full_path = :full_path AND folder_state_id = :state_id"
    result = await database.fetch_one(query=query, values={"user_id": user_id, "full_path": full_path, "state_id": active_state["id"]})
    return result


async def update_folder_parent_dir(folder_id, folder_name, folder_path, parent_dir):
    query = "UPDATE folders SET name = :folder_name, full_path = :folder_path, parent_directory_id = :parent_dir WHERE id = :folder_id RETURNING id"
    values = {"folder_id": folder_id, "folder_name": folder_name,
              "folder_path": folder_path, "parent_dir": parent_dir}
    result = await database.execute(query=query, values=values)
    return result


async def get_all_dir_except_children(full_path, parent_folder_id, user_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT id,full_path FROM folders \
        WHERE created_by_user = :user_id AND full_path NOT LIKE :full_path \
            AND folder_state_id = :state_id AND id != :parent_id \
        ORDER BY created_on"
    result = await database.fetch_all(query=query, values={"user_id": user_id, "full_path": full_path + "/%", "state_id": active_state["id"], "parent_id": parent_folder_id})
    return result


async def set_all_inactive(folder_id):
    folder_data = await get_full_path(folder_id=folder_id)
    active_state = await common.get_object_state_id("active")
    user_id = folder_data["created_by_user"]
    full_path = folder_data["full_path"]
    query = "SELECT id FROM folders WHERE created_by_user = :user_id AND full_path LIKE :full_path AND folder_state_id = :state_id"
    folder_list = await database.fetch_all(query=query, values={"user_id": user_id, "full_path": full_path + "%", "state_id": active_state["id"]})
    for i in folder_list:
        await set_inactive(i["id"])
    return folder_id


async def exists_and_inactive(folder_id, user_id):
    inactive_state = await common.get_object_state_id("inactive")
    query = "SELECT * FROM folders WHERE id = :folder_id AND created_by_user = :user_id AND folder_state_id = :state_id"
    result = await database.fetch_one(query=query, values={"user_id": user_id, "folder_id": folder_id, "state_id": inactive_state["id"]})
    return result


async def set_to_active(folder_id):
    query = "DELETE FROM folders_inactive WHERE folder_id = :folder_id RETURNING id"
    values = {"folder_id": folder_id}
    await database.execute(query=query, values=values)
    active_state = await common.get_object_state_id("active")
    query = "UPDATE folders SET folder_state_id = :state_id WHERE id = :folder_id RETURNING id"
    result = await database.execute(query=query, values={"folder_id": folder_id, "state_id": active_state["id"]})
    return result


async def get_all_folders_path(user_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT id,full_path FROM folders WHERE created_by_user = :user_id AND folder_state_id = :state_id ORDER BY created_on"
    result = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": active_state["id"]})
    return result


async def set_full_path(new_full_path, folder_id):
    query = "UPDATE folders SET full_path = :full_path WHERE id = :folder_id RETURNING id"
    result = await database.execute(query=query, values={"folder_id": folder_id, "full_path": new_full_path})
    return result


async def update_full_path_children(old_path_prepend, new_path_prepend, user_id):
    query = "SELECT * FROM folders WHERE created_by_user = :user_id AND full_path LIKE :full_path"
    folder_list = await database.fetch_all(query=query, values={"user_id": user_id, "full_path": old_path_prepend + "/%"})
    for i in folder_list:
        new_path = new_path_prepend + i["full_path"][len(old_path_prepend):]
        await set_full_path(new_full_path=new_path, folder_id=i["id"])


async def get_public_folders(user_id):
    active_state = await common.get_object_state_id("active")
    scope_id = await common.get_object_scope_id(scope="public")
    query = "SELECT folders.id, folders.name, folders.created_on, folders.full_path,\
        object_scopes.scope_type FROM folders \
        INNER JOIN object_scopes ON folders.folder_scope_id = object_scopes.id \
        WHERE folders.created_by_user = :user_id AND folders.folder_state_id = :state_id AND folders.folder_scope_id = :scope_id \
        ORDER BY folders.created_on DESC"
    result = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": active_state["id"], "scope_id": scope_id["id"]})
    return result


async def get_inactive_folders(user_id):
    inactive_state = await common.get_object_state_id("inactive")
    query = "SELECT folders.id, folders.name, folders_inactive.inactive_on, folders.full_path,\
        object_scopes.scope_type FROM folders \
        INNER JOIN object_scopes ON folders.folder_scope_id = object_scopes.id \
        INNER JOIN folders_inactive ON folders.id = folders_inactive.folder_id \
        WHERE folders.created_by_user = :user_id AND folders.folder_state_id = :state_id\
        ORDER BY folders_inactive.inactive_on DESC"
    result = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": inactive_state["id"]})
    return result
