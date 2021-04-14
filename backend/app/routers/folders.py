"""
//PATCH restore_folder/
PATCH rename_folder/
//PATCH change-folder-scope/
POST create_folder/
PATCH move_folder/
//PATCH move-folder-to-trash/
//DELETE folder/
"""

from ..queries import files
from fastapi import APIRouter, Query, File, UploadFile, Depends, Path
from fastapi.responses import Response
from ..auth import fastapi_users
from ..queries import folders, common
from typing import Optional


router = APIRouter()


@router.post("/create")
async def create_folder(
        folder_name: str,
        scope: str,
        parent_dir_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    scope_id = await common.get_object_scope_id(scope)
    active_state = await common.get_object_state_id("active")
    parent_dir_id = await folders.exists_and_active(folder_id=parent_dir_id, user_id=user.id)
    if parent_dir_id is None:
        return Response(status_code=404)
    folder_id = await folders.insert_folder(folder=folder_name, parent_dir_id=parent_dir_id["id"], state_id=active_state["id"], scope_id=scope_id["id"], user_id=user.id)
    print(folder_id)
    if folder_id == -1:
        return Response(status_code=409)
    result = await folders.get_folder_data(folder_id=folder_id, user_id=user.id, state_id=active_state["id"])
    return result


@router.patch("/move")
async def move_folder_to_folder(
        folder_id: int,
        new_parent_folder_id: int,
        user=Depends(fastapi_users.current_user(active=True)),):
    if folder_id == new_parent_folder_id:
        return Response(status_code=400)
    folder_id_active = await folders.exists_and_active(
        folder_id=folder_id, user_id=user.id)
    if folder_id_active is None:
        return Response(status_code=404)
    if folder_id_active["parent_directory_id"] == new_parent_folder_id:
        return folder_id
    new_parent_dir_id_active = await folders.exists_and_active(
        folder_id=new_parent_folder_id, user_id=user.id)
    if new_parent_dir_id_active is None:
        return Response(status_code=404)
    folder_id_full_path = folder_id_active["full_path"]
    new_parent_dir_full_path = new_parent_dir_id_active["full_path"]
    if folder_id_full_path in new_parent_dir_full_path:
        return Response(status_code=400)
    result = await folders.move(folder_id=folder_id, parent_dir_id=new_parent_folder_id)
    if result == -1:
        return Response(status_code=409)
    else:
        return result


@router.get("/")
async def get_folders_in_current_directory(
        current_dir_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    folder_exists = await folders.exists_and_active(folder_id=current_dir_id, user_id=user.id)
    if folder_exists is None:
        return Response(status_code=404)
    else:
        folders_list = await folders.get_folders_in_parent(parent_directory_id=current_dir_id)
        return folders_list


@router.get("/root")
async def get_folders_in_root(
        user=Depends(fastapi_users.current_user(active=True))):
    dir = await folders.get_root_dir(user_id=user.id)
    folders_list = await folders.get_folders_in_parent(parent_directory_id=dir["id"])
    return folders_list


@router.patch("/scope")
async def change_folder_scope(
        folder_id: int,
        scope: str,
        user=Depends(fastapi_users.current_user(active=True))):
    scope_id = await common.get_object_scope_id(scope)
    isfolder_and_active = await folders.exists_and_active(folder_id=folder_id, user_id=user.id)
    if isfolder_and_active is None:
        return Response(status_code=404)
    else:
        result = await folders.change_folder_scope(folder_id=folder_id, scope_id=scope_id["id"])
        return result


@router.patch("/inactive")
async def make_folder_inactive(
        folder_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    root_dir = await folders.get_root_dir(user_id=user.id)
    if root_dir["id"] == folder_id:
        return Response(status_code=400)
    isfolder_and_active = await folders.exists_and_active(folder_id=folder_id, user_id=user.id)
    if isfolder_and_active is None:
        return Response(status_code=404)
    else:
        result = await folders.set_all_inactive(folder_id=folder_id)
        return result


@router.get("/move-to-list")
async def get_all_path_except_children(
        folder_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    folder_exists = await folders.exists_and_active(folder_id=folder_id, user_id=user.id)
    if folder_exists is None:
        return Response(status_code=404)
    path_list = await folders.get_all_dir_except_children(full_path=folder_exists["full_path"], parent_folder_id=folder_exists["parent_directory_id"], user_id=user.id)
    return path_list


@router.patch("/active")
async def make_folder_active(
        folder_id: int,
        user=Depends(fastapi_users.current_user(active=True))):
    isfolder_and_inactive = await folders.exists_and_inactive(folder_id=folder_id, user_id=user.id)
    if isfolder_and_inactive is None:
        return Response(status_code=404)
    else:
        folder_id_path = isfolder_and_inactive["full_path"]
        active_folder_path = await folders.folderpath_constraint(full_path=folder_id_path, user_id=user.id)
        if active_folder_path is not None:
            return Response(status_code=409)
        result = await folders.set_to_active(folder_id=folder_id)
        return result


@router.get("/folder-create-list")
async def get_all_active_dir_path(
        user=Depends(fastapi_users.current_user(active=True))):
    result = await folders.get_all_folders_path(user_id=user.id)
    return result


@router.get("/public")
async def get_public_folders(user=Depends(fastapi_users.current_user(active=True))):
    folder_list = await folders.get_public_folders(user_id=user.id)
    return folder_list


@router.get("/inactive-folders")
async def get_inactive_folders(user=Depends(fastapi_users.current_user(active=True))):
    folder_list = await folders.get_inactive_folders(user_id=user.id)
    return folder_list


@router.get("/root-id")
async def get_root_dir_id(
        user=Depends(fastapi_users.current_user(active=True))):
    result = await folders.get_root_dir(user_id=user.id)
    return {"id": result["id"]}


@router.get("/{id}")
async def get_folder_by_id(
        state: str,
        id: int = Path(..., gt=0),
        user=Depends(fastapi_users.current_user(active=True))):
    state_id = await common.get_object_state_id(state=state)
    result = await folders.get_folder_data(
        folder_id=id, user_id=user.id, state_id=state_id["id"])
    if result is None:
        return Response(status_code=404)
    return result


@router.patch("/rename")
async def rename_folder(
        folder_id: int,
        new_name: str,
        user=Depends(fastapi_users.current_user(active=True))):
    folder_exists = await folders.exists_and_active(folder_id=folder_id, user_id=user.id)
    if folder_exists is None:
        return Response(status_code=404)
    last_slash = folder_exists["full_path"].rfind("/")
    parent_dir = folder_exists["parent_directory_id"]
    parent_path = folder_exists["full_path"][0:last_slash]
    suggested_path = parent_path + "/" + new_name
    constraint_violated = await folders.folderpath_constraint(
        full_path=suggested_path, user_id=user.id)
    if constraint_violated:
        return Response(status_code=409)
    result = await folders.update_folder_parent_dir(folder_id=folder_id, folder_name=new_name, folder_path=suggested_path, parent_dir=parent_dir)
    update_children = await folders.update_full_path_children(old_path_prepend=folder_exists["full_path"], new_path_prepend=suggested_path, user_id=user.id)
    return result
