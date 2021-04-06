from ..queries import files
from fastapi import APIRouter, Query, File, UploadFile, Depends
from fastapi.responses import Response
import uuid
from typing import Optional
from ..auth import fastapi_users
from ..queries import folders
from ..config.config import STORAGE_SERVICE
from ..config.s3 import aws_upload, generate_download_url

router = APIRouter()


@router.post("/upload")
async def upload_file(
        user=Depends(fastapi_users.current_user(active=True)),
        file: UploadFile = File(...),
        folder: Optional[str] = None,
        scope: Optional[str] = None):
    if folder is None:
        folder = "root"
    elif folder == "trash":
        return Response(status_code=400)
    parent_dir_id = await folders.exists(folder, user.id)
    if parent_dir_id is None:
        return Response(status_code=400)
    if scope is None:
        scope = "private"
    scope_id = await files.get_scope_id(scope)
    contentType = file.content_type
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
        content_type = await files.get_content_type(content_type=contentType)

        if not content_type:
            content_type_id = await files.add_content_type(content_type=contentType)
        else:
            content_type_id = content_type["id"]
        file_id = await files.insert_file(filename=file_name, uploaded_by=user.id, content_type=content_type_id,
                                          size=len(content), parent_dir=parent_dir_id["id"],
                                          scope=scope_id["id"])
        result = await files.insert_aws_file(file_id=file_id, aws_file_name=aws_file_name)
    return Response(status_code=201)


@router.patch("/star")
async def star_file(
        filename: str,
        folder: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    folder_id = folders.exists(folder, user.id)
    if folder_id is None:
        return Response(status_code=400)
    file = await files.exists_in_dir(filename, folder_id["id"], user.id)
    if file is not None:
        try:
            result = await files.starfile_insert(file['id'], user.id)
        except:
            result = await files.starfile_update(file_id=file['id'], user_id=user.id, is_starred=True)
    else:
        return Response(status_code=404)
    return Response(status_code=204)


@router.patch("/unstar")
async def unstar_file(
        filename: str,
        folder: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    folder_id = folders.exists(folder, user.id)
    if folder_id is None:
        return Response(status_code=400)
    file = await files.exists_in_dir(filename, folder_id["id"], user.id)
    if file is not None:
        result = await files.starfile_update(file_id=file['id'], user_id=user.id, is_starred=False)
    else:
        return Response(status_code=404)
    return Response(status_code=204)


@router.patch("/trash")
async def move_file_to_trash(
        filename: str,
        old_folder: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    old_folder_id = await folders.exists(old_folder, user.id)
    if old_folder_id is None:
        return Response(status_code=400)
    file = await files.exists_in_dir(filename, old_folder_id["id"], user.id)
    if file is None:
        return Response(status_code=400)
    current_state_id = file["file_state_id"]
    inactive_state = await files.get_state_id("inactive")
    inactive_state_id = inactive_state["id"]
    if current_state_id >= inactive_state_id:
        return Response(status_code=400)
    folder = "trash"
    if file is not None:
        folder = await folders.exists(folder, user.id)
        if folder is not None:
            try:
                await files.move(file["id"], folder["id"])
            except:
                return Response(status_code=409)
            await files.insert_inactive_file(file["id"], user.id, old_folder_id["id"])
            await files.update_file_state(file["id"], inactive_state_id)
            return Response(status_code=204)
        else:
            return Response(status_code=400)
    else:
        return Response(status_code=404)


# inactive check
@router.patch("/move")
async def move_file_to_folder(
        filename: str,
        old_folder: str,
        new_folder: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    if new_folder == "trash":
        return Response(status_code=400)
    old_folder_id = await folders.exists(old_folder, user.id)
    if old_folder_id is None:
        return Response(status_code=400)
    file = await files.exists_in_dir(filename, old_folder_id["id"], user.id)
    if file is not None:
        folder = await folders.exists(new_folder, user.id)
        if folder is not None:
            try:
                await files.move(file["id"], folder["id"])
            except:
                return Response(status_code=409)
            return Response(status_code=204)
        else:
            return Response(status_code=400)
    else:
        return Response(status_code=404)


@router.get("/download")
async def download_file(
    filename: str,
    folder: str,
    user=Depends(fastapi_users.current_user(active=True)),):
    folder_id = folders.exists(folder, user.id)
    if folder_id is None:
        return Response(status_code=400)
    file_data = await files.exists_in_dir(filename, folder_id["id"], user.id)
    if file_data is None:
        Response(status_code=404)
    file_name = await files.get_aws_file_name(file_data['id'])
    content_data = await files.get_content_type_by_id(file_data["content_type"])
    response = generate_download_url(
        object_key=file_name["aws_file_name"], expiry=3600)

    return {"download_url": response}


@router.patch("/rename")
async def rename_file(
        filename: str,
        folder: str,
        newfilename: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    folder_id = await folders.exists(folder, user.id)
    if folder_id is None:
        return Response(status_code=400)
    file_data = await files.exists_in_dir(filename, folder_id["id"], user.id)
    if file_data is None:
        return Response(status_code=400)
    new_file_exists = await files.exists_in_dir(newfilename, file_data["parent_directory_id"], user.id)
    if new_file_exists:
        return Response(status_code=409)
    else:
        result = await files.update_name(newfilename=newfilename, file_id=file_data["id"])
    if result:
        return Response(status_code=204)


@router.delete("")
async def delete_file(
        filename: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    file_data = await files.exists(filename, user.id)
    if file_data is None:
        return Response(status_code=400)
    deleted_state = await files.get_state_id("deleted")
    deleted_state_id = deleted_state["id"]
    destroyed_state = await files.get_state_id("destroyed")
    destroyed_state_id = destroyed_state["id"]
    current_state_id = file_data["file_state_id"]
    if current_state_id == destroyed_state_id:
        return Response(status_code=400)
    result = await files.update_file_state(file_data["id"], deleted_state_id)
    if result:
        await files.insert_deleted_files(file_data["id"], user.id)
        return Response(status_code=204)


@router.patch("/restore")
async def restore_file(
        filename: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    folder_id = await folders.exists("trash", user.id)
    if folder_id is None:
        return Response(status_code=400)
    file = await files.exists_in_dir(filename, folder_id["id"], user.id)
    if file is None:
        return Response(status_code=400)
    old_folder = await files.get_inactive_file_old_dir(file["id"])
    if old_folder is None:
        return Response(status_code=400)
    active_state = await files.get_state_id("active")
    active_state_id = active_state["id"]
    if file is not None:
        try:
            await files.move(file["id"], old_folder["id"])
        except:
            return Response(status_code=409)
        await files.delete_inactive_file(file["id"])
        await files.update_file_state(file["id"], active_state_id)
        return Response(status_code=204)
    else:
        return Response(status_code=404)


@router.get("/")
async def get_files(
        directory: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    active_state = await files.get_state_id("active")
    folder_id = await folders.exists(directory, user.id)
    if folder_id is None:
        return Response(status_code=400)
    result = await files.get_files(active_state["id"], folder_id["id"])
    return result


@router.get("/starred-files")
async def get_starred_files(
        user=Depends(fastapi_users.current_user(active=True)),):
    active_state = await files.get_state_id("active")
    result = await files.get_starred_files(active_state["id"], user.id)
    return result


@router.get("/inactive-files")
async def get_inactive_files(
        user=Depends(fastapi_users.current_user(active=True)),):
    inactive_state = await files.get_state_id("inactive")
    result = await files.get_inactive_files(inactive_state["id"], user.id)
    return result


@router.patch("/scope")
async def change_file_scope(
        filename: str,
        folder: str,
        scope: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    file = await files.exists(filename, user.id)
    if file is None:
        return Response(status_code=404)
    new_scope = await files.get_scope_id(scope=scope)
    if new_scope is None:
        return Response(status_code=400)
    result = await files.change_scope(file["id"], new_scope["id"])
    return result
