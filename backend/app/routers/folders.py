"""
//PATCH restore_folder/
PATCH rename_folder/
//PATCH change-folder-scope/
POST create_folder/
PATCH move_folder/
//PATCH move-folder-to-trash/
//DELETE folder/ 
"""

from backend.app.routers.files import move_file_to_folder
from ..queries import files
from fastapi import APIRouter, Query, File, UploadFile, Depends
from fastapi.responses import Response
from ..auth import fastapi_users
from ..queries import folders
from typing import Optional


router = APIRouter()


@router.post("/create")
async def create_folder(
        folder: str,
        scope: str,
        parent_dir: Optional[str] = None,
        user=Depends(fastapi_users.current_user(active=True))):
    scope_id = await files.get_scope_id(scope)
    parent_dir_id = await folders.exists(parent_dir, user.id)
    if parent_dir_id is None:
        parent_dir_id = await folders.exists("root", user.id)
    try:
        folder_id = await folders.insert_folder(folder, user.id, parent_dir_id["id"], scope_id["id"])
    except:
        return Response(status_code=409)
    return Response(status_code=204)


# @router.patch("/rename")
@router.patch("/move")
async def move_folder_to_folder(
        folder: str,
        parent_dir_folder: str,
        user=Depends(fastapi_users.current_user(active=True)),):
    if folder == "trash" or parent_dir_folder == "trash":
        return Response(status_code=400)
    folder_id = folders.exists(folder, user.id)
    parent_dir_id = folders.exists(parent_dir_folder, user.id)
    if folder_id is None or parent_dir_folder is None:
        return Response(status_code=400)
    else:
        try:
            folder_id = await folders.move(folder=folder_id, parent_directory=parent_dir_id)

        except:
            return Response(status_code=409)
    return Response(status_code=204)
