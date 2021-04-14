import re
from fastapi.param_functions import Query
from sqlalchemy.sql.expression import false
from ..queries import files, folders, common
from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import Response
import uuid
from typing import Optional
from ..auth import fastapi_users
from ..config.config import STORAGE_SERVICE
from ..config.s3 import aws_upload, generate_download_url

router = APIRouter()


@router.post("/upload")
async def upload_file(
        folder_id: int,
        scope: str,
        file: UploadFile = File(...),
        user=Depends(fastapi_users.current_user(active=True))):
    parent_dir_id = await folders.exists_and_active(folder_id=folder_id, user_id=user.id)
    if parent_dir_id is None:
        return Response(status_code=404)
    scope_id = await common.get_object_scope_id(scope=scope)
    file_name = file.filename
    old_file = await files.exists_in_dir(filename=file_name, folder_id=parent_dir_id["id"], user_id=user.id)
    if old_file:
        return Response(status_code=409)
    aws_file_name = ''.join([str(uuid.uuid4().hex) + "_", file_name])

    content = file.file.read()

    if STORAGE_SERVICE == 'aws':
        response = aws_upload(filename=aws_file_name,
                              file_content=content, expiration=3600)

    if response.status_code == 204:
        file_id = await files.insert_file(filename=file_name, uploaded_by=user.id,
                                          size=len(content), parent_dir=parent_dir_id["id"],
                                          scope=scope_id["id"])
        aws_result = await files.insert_aws_file(file_id=file_id, aws_file_name=aws_file_name)
        result = await files.get_file_data(file_id=file_id, user_id=user.id)
        return result


@router.patch("/star")
async def star_file(
        file_id: int,
        user=Depends(fastapi_users.current_user(active=True)),):
    file = await files.exists_and_public(file_id=file_id)
    if file is None:
        file = await files.exists(file_id=file_id, user_id=user.id)
        if file is None:
            return Response(status_code=404)
    active_state = await common.get_object_state_id("active")
    if file["file_state_id"] != active_state["id"]:
        return Response(status_code=404)
    result = await files.starfile_insert(file_id=file['id'], user_id=user.id, is_starred=True)
    if result == -1:
        result = await files.starfile_update(file_id=file['id'], user_id=user.id, is_starred=True)
    return Response(status_code=204)


@router.patch("/unstar")
async def unstar_file(
        file_id: int,
        user=Depends(fastapi_users.current_user(active=True)),):
    file = await files.exists_and_public(file_id=file_id)
    if file is None:
        file = await files.exists(file_id=file_id, user_id=user.id)
        if file is None:
            return Response(status_code=404)
    active_state = await common.get_object_state_id("active")
    if file["file_state_id"] != active_state["id"]:
        return Response(status_code=404)
    result = await files.starfile_update(file_id=file['id'], user_id=user.id, is_starred=False)
    if result is None:
        return Response(status_code=404)
    else:
        return Response(status_code=204)


@router.patch("/inactive")
async def make_file_inactive(
        file_id: int,
        user=Depends(fastapi_users.current_user(active=True)),):
    file_exists = await files.exists_and_active(file_id=file_id, user_id=user.id)
    if file_exists is None:
        return Response(status_code=404)
    else:
        result = await files.set_inactive(file_id=file_id)
        if result == -1:
            return Response(status_code=404)
        return result


@router.patch("/move")
async def move_file_to_folder(
        file_id: int,
        folder_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    parent_dir_id = await folders.exists_and_active(folder_id=folder_id, user_id=user.id)
    if parent_dir_id is None:
        return Response(status_code=404)
    file = await files.exists(file_id=file_id, user_id=user.id)
    if file is None:
        return Response(status_code=404)
    active_state = await common.get_object_state_id("active")
    if file["file_state_id"] != active_state["id"]:
        return Response(status_code=404)
    old_file = await files.exists_in_dir(filename=file["name"], folder_id=parent_dir_id["id"], user_id=user.id)
    if old_file:
        return Response(status_code=409)
    if file["parent_directory_id"] == folder_id:
        return file_id
    result = await files.move(file_id=file_id, folder_id=folder_id)
    return result


@router.get("/download")
async def download_file(
        file_id: int,
        user=Depends(fastapi_users.current_user(active=True)),):
    file = await files.exists_and_public(file_id=file_id)
    if file is None:
        file = await files.exists(file_id=file_id, user_id=user.id)
        if file is None:
            return Response(status_code=404)
    active_state = await common.get_object_state_id("active")
    if file["file_state_id"] != active_state["id"]:
        return Response(status_code=404)
    file_name = await files.get_aws_file_name(file['id'])
    if STORAGE_SERVICE == 'aws':
        response = generate_download_url(
            object_key=file_name["aws_file_name"], expiry=3600)

    return {"download_url": response}


@router.patch("/rename")
async def rename_file(
        file_id: int,
        newfilename: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    file_data = await files.exists_and_active(file_id=file_id, user_id=user.id)
    if file_data is None:
        return Response(status_code=404)
    new_file_exists = await files.exists_in_dir(newfilename, file_data["parent_directory_id"], user.id)
    if new_file_exists:
        return Response(status_code=409)
    else:
        result = await files.update_name(newfilename=newfilename, file_id=file_data["id"])
        return result


# @router.delete("")
# async def delete_file(
#         filename: str,
#         user=Depends(fastapi_users.current_user(active=True)),):
#     file_data = await files.exists(filename, user.id)
#     if file_data is None:
#         return Response(status_code=400)
#     deleted_state = await files.get_state_id("deleted")
#     deleted_state_id = deleted_state["id"]
#     destroyed_state = await files.get_state_id("destroyed")
#     destroyed_state_id = destroyed_state["id"]
#     current_state_id = file_data["file_state_id"]
#     if current_state_id == destroyed_state_id:
#         return Response(status_code=400)
#     result = await files.update_file_state(file_data["id"], deleted_state_id)
#     if result:
#         await files.insert_deleted_files(file_data["id"], user.id)
#         return Response(status_code=204)


# @router.patch("/restore")
# async def restore_file(
#         filename: str,
#         user=Depends(fastapi_users.current_user(active=True)),):
#     folder_id = await folders.exists("trash", user.id)
#     if folder_id is None:
#         return Response(status_code=400)
#     file = await files.exists_in_dir(filename, folder_id["id"], user.id)
#     if file is None:
#         return Response(status_code=400)
#     old_folder = await files.get_inactive_file_old_dir(file["id"])
#     if old_folder is None:
#         return Response(status_code=400)
#     active_state = await files.get_state_id("active")
#     active_state_id = active_state["id"]
#     if file is not None:
#         try:
#             await files.move(file["id"], old_folder["id"])
#         except:
#             return Response(status_code=409)
#         await files.delete_inactive_file(file["id"])
#         await files.update_file_state(file["id"], active_state_id)
#         return Response(status_code=204)
#     else:
#         return Response(status_code=404)


@router.get("/")
async def get_files_in_current_directory(
        current_dir_id: int,
        user=Depends(fastapi_users.current_user(active=True)),):
    folder_exists = await folders.exists_and_active(folder_id=current_dir_id, user_id=user.id)
    if folder_exists is None:
        return Response(status_code=404)
    else:
        file_list = await files.get_files_in_parent(parent_directory_id=current_dir_id, user_id=user.id)
        return file_list


@router.get("/public")
async def get_public_files(user=Depends(fastapi_users.current_user(active=True))):
    file_list = await files.get_public_files(user_id=user.id)
    return file_list


@router.patch("/active")
async def make_file_active(
        file_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    isfile_and_inactive = await files.exists_and_inactive(file_id=file_id, user_id=user.id)
    if isfile_and_inactive is None:
        return Response(status_code=404)
    else:
        result = await files.set_to_active(file_id=file_id)
        return result


@router.get("/inactive-files")
async def get_inactive_files(user=Depends(fastapi_users.current_user(active=True))):
    file_list = await files.get_inactive_files(user_id=user.id)
    return file_list


@router.get("/starred")
async def get_starred_files(
        user=Depends(fastapi_users.current_user(active=True)),):
    active_state = await files.get_state_id("active")
    result = await files.get_starred_files(user_id=user.id)
    return result


# @router.get("/inactive-files")
# async def get_inactive_files(
#         user=Depends(fastapi_users.current_user(active=True)),):
#     inactive_state = await files.get_state_id("inactive")
#     result = await files.get_inactive_files(inactive_state["id"], user.id)
#     return result


@router.patch("/scope")
async def change_file_scope(
        file_id: int,
        scope: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    file = await files.exists(file_id=file_id, user_id=user.id)
    if file is None:
        return Response(status_code=404)
    new_scope = await files.get_scope_id(scope=scope)
    if new_scope is None:
        return Response(status_code=400)
    result = await files.change_scope(file_id=file["id"], scope_id=new_scope["id"], scope_type=scope, user_id=user.id)
    return result


@router.get("/root")
async def get_files_in_root(
        user=Depends(fastapi_users.current_user(active=True))):
    dir = await folders.get_root_dir(user_id=user.id)
    file_list = await files.get_files_in_parent(parent_directory_id=dir["id"], user_id=user.id)
    return file_list
