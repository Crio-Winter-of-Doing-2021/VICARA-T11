from sqlalchemy.sql.functions import user
from ..config.db import database
from ..queries import common

# async def get_folder_id(folder=None, user = None):
#     if folder is None:
#         folder = "root"

#     query = "SELECT id FROM folders WHERE name = :name AND created_by_user = :id"
#     result = await database.fetch_one(query=query, values={"id": user, "name" : folder})
#     return result


async def insert_file(filename, uploaded_by, size,
                      parent_dir, scope):
    active_state = await common.get_object_state_id("active")
    size_GB = size / (1024 ** 3)
    files_query = "INSERT INTO files (name, uploaded_by, size_in_gb, parent_directory_id, \
         file_state_id, file_scope_id) VALUES (:name, :uploaded_by, :size_in_gb, :parent_directory_id, \
         :file_state_id, :file_scope_id) RETURNING id"
    files_values = {"name": filename, "uploaded_by": uploaded_by, "size_in_gb": size_GB,
                    "parent_directory_id": parent_dir, "file_state_id": active_state["id"], "file_scope_id": scope}
    result = await database.execute(query=files_query, values=files_values)
    return result


async def insert_aws_file(file_id, aws_file_name):
    query = "INSERT INTO aws_files (file_id, aws_file_name) VALUES (:file_id, :aws_file_name)"
    values = {"file_id": file_id, "aws_file_name": aws_file_name}
    await database.execute(query=query, values=values)


async def starfile_insert(file_id, user_id, is_starred):

    query = "INSERT INTO files_starred (file_id, starred_by, is_starred) VALUES (:file_id, :user_id, :is_starred) RETURNING file_id"
    values = {"file_id": file_id, "user_id": user_id, "is_starred": is_starred}
    try:
        await database.execute(query=query, values=values)
    except:
        return -1


async def starfile_update(file_id, user_id, is_starred):

    query = "UPDATE files_starred SET is_starred = :is_starred WHERE file_id = :file_id AND starred_by = :user_id RETURNING file_id"
    values = {"is_starred": is_starred, "file_id": file_id, "user_id": user_id}
    return await database.execute(query=query, values=values)


async def exists(file_id, user_id):
    query = "SELECT * FROM files WHERE id = :file_id AND uploaded_by = :user_id"
    result = await database.fetch_one(query=query, values={"user_id": user_id, "file_id": file_id})
    return result


async def move(file_id, folder_id):
    query = "UPDATE files SET parent_directory_id = :folder_id WHERE id = :file_id RETURNING id"
    values = {"file_id": file_id, "folder_id": folder_id}
    return await database.execute(query=query, values=values)


async def update_name(newfilename, file_id):
    query = "UPDATE files SET name = :name WHERE id = :file_id RETURNING id"
    values = {"name": newfilename, "file_id": file_id}
    return await database.execute(query=query, values=values)


async def get_aws_file_name(file_id):
    query = "SELECT aws_file_name FROM aws_files WHERE file_id = :id"
    result = await database.fetch_one(query=query, values={"id": file_id})
    return result


async def get_content_type(content_type=None):
    query = "SELECT id FROM content_types WHERE content_type = :content_type"
    result = await database.fetch_one(query=query, values={"content_type": content_type})
    return result


async def add_content_type(content_type=None):
    query = "INSERT INTO content_types (content_type) VALUES (:content_type) RETURNING id"
    values = {"content_type": content_type}
    return await database.execute(query=query, values=values)


async def get_content_type_by_id(content_type_id=None):
    query = "SELECT content_type FROM content_types WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": content_type_id})
    return result


async def get_state_id(state):
    query = "SELECT id FROM object_states WHERE state_type = :state"
    result = await database.fetch_one(query=query, values={"state": state})
    return result


async def update_file_state(file_id, state_id):
    query = "UPDATE files SET file_state_id = :state_id WHERE id = :file_id RETURNING id"
    values = {"file_id": file_id, "state_id": state_id}
    return await database.execute(query=query, values=values)


async def insert_inactive_file(file_id, user_id, parent_dir_id):
    query = "INSERT INTO files_inactive (file_id, inactive_by_user, deleted_from_parent_dir) \
        VALUES (:file_id, :user_id, :parent_dir) RETURNING id"
    values = {"file_id": file_id, "user_id": user_id,
              "parent_dir": parent_dir_id}
    return await database.execute(query=query, values=values)


async def get_files(state_id, folder_id):
    query = "SELECT name, uploaded_on, size_in_gb, file_scope_id FROM files \
        WHERE parent_directory_id = :folder_id AND file_state_id = :state_id ORDER BY uploaded_on DESC"
    result = await database.fetch_all(query=query, values={"folder_id": folder_id, "state_id": state_id})
    return result


async def get_starred_files(user_id):
    query = "SELECT files_starred.file_id\
        FROM files_starred \
        INNER JOIN files ON files_starred.file_id = files.id \
        WHERE files_starred.starred_by = :user_id AND files_starred.is_starred = True \
        ORDER BY files.uploaded_on DESC"
    file_list = await database.fetch_all(query=query, values={"user_id": user_id})
    result = []
    for file in file_list:
        file = await get_file_data(file_id=file["file_id"], user_id=user_id)
        result.append(file)
    return result


async def get_inactive_files(state_id, user_id):
    query = "SELECT files.name, files.size_in_gb, files.file_scope_id, files_inactive.inactive_on \
        FROM files \
        INNER JOIN files_inactive ON files.uploaded_by = files_inactive.inactive_by_user \
        WHERE files.uploaded_by = :user_id AND files.file_state_id = :state_id\
        ORDER BY files_inactive.inactive_on DESC"
    result = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": state_id})
    return result


async def get_inactive_file_old_dir(file_id):
    query = "SELECT * FROM files_inactive \
        WHERE file_id = :file_id"
    result = await database.fetch_one(query=query, values={"file_id": file_id})
    return result


async def delete_inactive_file(file_id):
    query = "DELETE FROM files_inactive  \
        WHERE file_id = :file_id"
    result = await database.fetch_one(query=query, values={"file_id": file_id})
    return result


async def insert_deleted_files(file_id, user_id):
    query = "INSERT INTO files_deleted (file_id, deleted_by_user) \
        VALUES (:file_id, :user_id) RETURNING id"
    values = {"file_id": file_id, "user_id": user_id}
    return await database.execute(query=query, values=values)


async def get_scope_id(scope):
    query = "SELECT id FROM object_scopes WHERE scope_type = :scope"
    result = await database.fetch_one(query=query, values={"scope": scope})
    return result


async def change_scope(file_id, scope_id, scope_type, user_id):
    query = "UPDATE files SET  file_scope_id = :scope_id WHERE id = :file_id RETURNING id"
    values = {"file_id": file_id, "scope_id": scope_id}
    result = await database.execute(query=query, values=values)
    if result and scope_type == 'private':
        await unstar_all_by_file_id_exclude_user(file_id=file_id, user_id=user_id)
    return result


async def get_files_in_parent(parent_directory_id, user_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT files.id, files.name, files.size_in_gb, files.uploaded_on, files.parent_directory_id,\
        folders.full_path, object_scopes.scope_type FROM files \
        INNER JOIN object_scopes ON files.file_scope_id = object_scopes.id \
        INNER JOIN folders ON files.parent_directory_id = folders.id \
        WHERE files.parent_directory_id = :folder_id AND folders.folder_state_id = :state_id AND files.file_state_id = :state_id\
        ORDER BY files.uploaded_on DESC"
    files = await database.fetch_all(query=query, values={"folder_id": parent_directory_id, "state_id": active_state["id"]})
    result_files = []
    for file in files:
        file_dict = dict(file)
        result = await is_file_starred(file_id=file["id"], user_id=user_id)
        if result is None:
            file_dict["is_starred"] = 0
        else:
            file_dict["is_starred"] = 1
        result_files.append(file_dict)
    return result_files


async def is_file_starred(file_id, user_id):
    is_starred = True
    query = "SELECT * FROM files_starred WHERE  file_id = :file_id AND starred_by = :user_id AND is_starred = :is_starred"
    values = {"file_id": file_id, "user_id": user_id, "is_starred": is_starred}
    result = await database.fetch_one(query=query, values=values)
    return result


async def exists_and_public(file_id):
    scope_id = await common.get_object_scope_id(scope="public")
    query = "SELECT * FROM files WHERE id = :file_id AND file_scope_id = :scope_id"
    result = await database.fetch_one(query=query, values={"scope_id": scope_id["id"], "file_id": file_id})
    return result


async def unstar_all_by_file_id_exclude_user(file_id, user_id):
    is_starred = False
    query = "UPDATE files_starred SET is_starred = :is_starred WHERE file_id = :file_id AND starred_by != :user_id"
    values = {"is_starred": is_starred, "file_id": file_id, "user_id": user_id}
    return await database.execute(query=query, values=values)


async def exists_in_dir(filename, folder_id, user_id):
    query = "SELECT * FROM files WHERE name = :name AND uploaded_by = :id AND parent_directory_id = :folder_id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name": filename, "folder_id": folder_id})
    return result


async def set_inactive(file_id):
    query = "INSERT INTO files_inactive (file_id) VALUES (:file_id) RETURNING id"
    values = {"file_id": file_id}
    try:
        await database.execute(query=query, values=values)
    except:
        return -1
    inactive_state = await common.get_object_state_id("inactive")
    query = "UPDATE files SET file_state_id = :state_id WHERE id = :file_id RETURNING id"
    result = await database.execute(query=query, values={"file_id": file_id, "state_id": inactive_state["id"]})
    await unstar_all_by_file_id(file_id=file_id)
    return result


async def unstar_all_by_file_id(file_id):
    is_starred = False
    query = "UPDATE files_starred SET is_starred = :is_starred WHERE file_id = :file_id"
    values = {"is_starred": is_starred, "file_id": file_id}
    return await database.execute(query=query, values=values)


async def exists_and_active(file_id, user_id):
    active = await common.get_object_state_id(state="active")
    query = "SELECT * FROM files WHERE id = :file_id AND uploaded_by = :user_id AND file_state_id = :state_id"
    result = await database.fetch_one(query=query, values={"state_id": active["id"], "file_id": file_id, "user_id": user_id})
    return result


async def get_file_data(file_id, user_id):
    active_state = await common.get_object_state_id("active")
    query = "SELECT files.id, files.name, files.size_in_gb, files.uploaded_on, files.parent_directory_id,\
        folders.full_path, object_scopes.scope_type FROM files \
        INNER JOIN object_scopes ON files.file_scope_id = object_scopes.id \
        INNER JOIN folders ON files.parent_directory_id = folders.id \
        WHERE files.id = :file_id AND files.file_state_id = :state_id\
        "
    file = await database.fetch_one(query=query, values={"file_id": file_id, "state_id": active_state["id"]})
    file_dict = dict(file)
    result = await is_file_starred(file_id=file["id"], user_id=user_id)
    if result is None:
        file_dict["is_starred"] = 0
    else:
        file_dict["is_starred"] = 1
    return file_dict


async def get_public_files(user_id):
    active_state = await common.get_object_state_id("active")
    scope_id = await common.get_object_scope_id(scope="public")
    query = "SELECT files.id, files.name, files.size_in_gb, files.uploaded_on, files.parent_directory_id,\
            folders.full_path, object_scopes.scope_type FROM files \
            INNER JOIN object_scopes ON files.file_scope_id = object_scopes.id \
            INNER JOIN folders ON files.parent_directory_id = folders.id \
            WHERE files.uploaded_by = :user_id AND files.file_state_id = :state_id AND files.file_scope_id = :scope_id\
            ORDER BY files.uploaded_on DESC"
    files = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": active_state["id"], "scope_id": scope_id["id"]})
    return files


async def get_inactive_files(user_id):
    inactive_state = await common.get_object_state_id("inactive")
    query = "SELECT files.id, files.name, files.size_in_gb, files_inactive.inactive_on, files.parent_directory_id,\
            folders.full_path, object_scopes.scope_type FROM files \
            INNER JOIN object_scopes ON files.file_scope_id = object_scopes.id \
            INNER JOIN folders ON files.parent_directory_id = folders.id \
            INNER JOIN files_inactive ON files.id = files_inactive.file_id \
            WHERE files.uploaded_by = :user_id AND files.file_state_id = :state_id\
            ORDER BY files_inactive.inactive_on DESC"
    files = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": inactive_state["id"], })
    return files


async def exists_and_inactive(file_id, user_id):
    inactive_state = await common.get_object_state_id("inactive")
    query = "SELECT * FROM files WHERE id = :file_id AND uploaded_by = :user_id AND file_state_id = :state_id"
    result = await database.fetch_one(query=query, values={"user_id": user_id, "file_id": file_id, "state_id": inactive_state["id"]})
    return result


async def set_to_active(file_id):
    query = "DELETE FROM files_inactive WHERE file_id = :file_id RETURNING id"
    values = {"file_id": file_id}
    await database.execute(query=query, values=values)
    active_state = await common.get_object_state_id("active")
    query = "UPDATE files SET file_state_id = :state_id WHERE id = :file_id RETURNING id"
    result = await database.execute(query=query, values={"file_id": file_id, "state_id": active_state["id"]})
    return result
