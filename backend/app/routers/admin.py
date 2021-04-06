# from ..queries import files
# from ..models.admin_route import StorageLimitModel
# from fastapi import APIRouter, Query, File, UploadFile, Depends
# from fastapi.responses import Response
# import uuid
# from typing import Optional
# from ..auth import fastapi_users
# from ..queries import users
# from ..config.config import STORAGE_SERVICE
# from ..config.s3 import aws_upload, generate_preview_url

# router = APIRouter()


# @router.patch("/user/storage_limit")
# async def change_storage_limit(
#     payload: StorageLimitModel,
#     admin=Depends(fastapi_users.current_user(active=True, superuser=True)),
# ):
#     new_storage_limit = payload.storage_limit
#     email = payload.email
#     user = await users.get_user(email=email)
#     user_id = user["id"]
#     object_state_deleted = files.is_deleted_state(state="deleted")["id"]
#     current_space = await users.get_current_space(user_id=user_id, state=object_state_deleted)
#     if current_space[] > new_storage_limit:
#         return {"error": "Free up some space using permanent_delete"}
