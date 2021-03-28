from ..config.db import database



# async def get_folder_id(folder=None, user = None):
#     if folder is None:
#         folder = "root"
    
#     query = "SELECT id FROM folders WHERE name = :name AND created_by_user = :id"
#     result = await database.fetch_one(query=query, values={"id": user, "name" : folder})
#     return result

async def insert_file(filename=None, uploaded_by = None, size = None,
parent_dir = None, scope=None):
    size_GB = size / (1024 ** 3)
    files_query = "INSERT INTO files (name, uploaded_by, size_in_GB, parent_directory_id, \
         file_state_id, file_scope_id) VALUES (:name, :uploaded_by, :size_in_GB, :parent_directory_id, \
         :file_state_id, :file_scope_id) RETURNING id"
    files_values = {"name" : filename, "uploaded_by": uploaded_by, "size_in_GB" : size_GB, 
                "parent_directory_id": parent_dir, "file_state_id" : 1, "file_scope_id" : scope }
    result = await database.execute(query=files_query, values=files_values)
    return result
    

async def insert_aws_file(file_id = None, aws_file_name = None):
    query = "INSERT INTO aws_files (file_id, aws_file_name) VALUES (:file_id, :aws_file_name)"
    values = {"file_id" : file_id, "aws_file_name" : aws_file_name}
    await database.execute(query=query, values=values)


async def starfile(file_id, user_id):

    query = "INSERT INTO files_starred (file_id, starred_by) VALUES (:file_id, :user_id) RETURNING file_id"
    values = {"file_id" : file_id, "user_id" : user_id }
    return await database.execute(query=query, values=values)

async def exists(filename, user_id):
    query = "SELECT id FROM files WHERE name = :name AND uploaded_by = :id"
    result = await database.fetch_one(query=query, values={"id": user_id, "name" : filename})
    return result

async def move(file_id, folder_id):
    query = "UPDATE files SET parent_directory_id = :folder_id WHERE id = :file_id"
    values = {"file_id" : file_id, "folder_id" : folder_id }
    return await database.execute(query=query, values=values)

async def get_aws_file_name(file_id):
    query = "SELECT aws_file_name FROM aws_files WHERE file_id = :id"
    result = await database.fetch_one(query=query, values={"id": file_id})
    return result

