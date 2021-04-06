from ..config.db import database


# async def get_folder_id(folder=None, user = None):
#     if folder is None:
#         folder = "root"

#     query = "SELECT id FROM folders WHERE name = :name AND created_by_user = :id"
#     result = await database.fetch_one(query=query, values={"id": user, "name" : folder})
#     return result

async def insert_file(filename=None, uploaded_by=None, size=None, content_type=None,
                      parent_dir=None, scope=None):
    size_GB = size / (1024 ** 3)
    files_query = "INSERT INTO files (name, content_type, uploaded_by, size_in_GB, parent_directory_id, \
         file_state_id, file_scope_id) VALUES (:name, :content_type, :uploaded_by, :size_in_GB, :parent_directory_id, \
         :file_state_id, :file_scope_id) RETURNING id"
    files_values = {"name": filename, "content_type": content_type, "uploaded_by": uploaded_by, "size_in_GB": size_GB,
                    "parent_directory_id": parent_dir, "file_state_id": 1, "file_scope_id": scope}
    result = await database.execute(query=files_query, values=files_values)
    return result


async def insert_aws_file(file_id=None, aws_file_name=None):
    query = "INSERT INTO aws_files (file_id, aws_file_name) VALUES (:file_id, :aws_file_name)"
    values = {"file_id": file_id, "aws_file_name": aws_file_name}
    await database.execute(query=query, values=values)


async def starfile_insert(file_id, user_id):

    query = "INSERT INTO files_starred (file_id, starred_by) VALUES (:file_id, :user_id) RETURNING file_id"
    values = {"file_id": file_id, "user_id": user_id}
    return await database.execute(query=query, values=values)


async def starfile_update(file_id, user_id, is_starred):

    query = "UPDATE files_starred SET is_starred = :is_starred WHERE file_id = :file_id AND starred_by = :user_id RETURNING file_id"
    values = {"is_starred": is_starred, "file_id": file_id, "user_id": user_id}
    return await database.execute(query=query, values=values)


async def exists(filename, user_id):
    query = "SELECT * FROM files WHERE name = :name AND uploaded_by = :id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name": filename})
    return result


async def exists_in_dir(filename, folder_id, user_id):
    query = "SELECT * FROM files WHERE name = :name AND uploaded_by = :id AND parent_directory_id = :folder_id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name": filename, "folder_id": folder_id})
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


async def get_starred_files(state_id, user_id):
    query = "SELECT files.name, files.uploaded_on, files.size_in_gb, files.file_scope_id \
        FROM files \
        INNER JOIN files_starred ON files.uploaded_by = files_starred.starred_by \
        WHERE files_starred.starred_by = :user_id AND files.file_state_id = :state_id AND files_starred.is_starred = True \
        ORDER BY files.uploaded_on DESC"
    result = await database.fetch_all(query=query, values={"user_id": user_id, "state_id": state_id})
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


async def change_scope(file_id, scope_id):
    query = "UPDATE files SET  scope_id = :scope_id WHERE id = :file_id RETURNING id"
    values = {"file_id": file_id, "scope_id": scope_id}
    result = await database.fetch_one(query=query, values=values)
    return result
