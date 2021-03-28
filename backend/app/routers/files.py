from ..queries import files
from fastapi import APIRouter, Query, File, UploadFile, Depends
from fastapi.responses import Response
import boto3
import requests
from botocore.exceptions import ClientError
import uuid
from typing import Optional
from ..auth import fastapi_users
from ..queries import folders

router = APIRouter()

def generate_presigned_url(object_key=None, expiry=3600):

    client = boto3.client("s3",
                             region_name="ap-south-1",
                             aws_access_key_id="AKIARLI5GU2HE5S2O6M6",
                             aws_secret_access_key="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",
                             )
    try:
        response = client.generate_presigned_url('get_object',
                                                  Params={'Bucket': 'nathanbucket123','Key': object_key},
                                                  ExpiresIn=expiry)
        return response
    except ClientError as e:
        print(e)

def create_presigned_post(filename=None, bucket_name=None, object_name=None,
                          fields=None, conditions=None, expiration=3600):

    # Generate a presigned S3 POST URL
    s3_client = boto3.client("s3",
                             region_name="ap-south-1",
                             aws_access_key_id="AKIARLI5GU2HE5S2O6M6",
                             aws_secret_access_key="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",
                             )
    try:
        response = s3_client.generate_presigned_post(Bucket="nathanbucket123",
                                                     Key=filename,
                                                     ExpiresIn=3600)
    except ClientError as e:
        return None

    # The response contains the presigned URL and required fields
    return response




@router.post("/upload")
async def upload_file(
    user=Depends(fastapi_users.get_current_active_user),
    file: UploadFile = File(...),
    filename: Optional[str] = None,
    folder: Optional[str] = None,
    scope: Optional[int] = Query(1, ge=1, le=2)  #  needs validation
    ):
    if filename is None:
        file_name = file.filename
    else:
        dot_index = file.filename.rfind(".")
        extension = file.filename[dot_index:]
        file_name = filename + extension
    aws_file_name = ''.join([str(uuid.uuid4().hex) + "_", file_name])
    parent_dir_id = await folders.exists(folder, user.id)

    if parent_dir_id is None:
        return {"error" : "Folder does not exist"}
    
    resp = create_presigned_post(filename=aws_file_name)

    content = file.file.read()
    


    # Extract the URL and other fields from the response
    post_url = resp['url']
    data = resp['fields']
    # Upload the file using requests module
    response = requests.post(url=post_url, data=data,
                             files={'file': content})

    if response.status_code == 204:
        file_id = await files.insert_file(filename=file_name, uploaded_by = user.id, 
                    size = len(content), parent_dir = parent_dir_id["id"],
                    scope=scope)
        result = await files.insert_aws_file(file_id=file_id, aws_file_name=aws_file_name)
    return Response(status_code=201)

@router.post("/star-action")
async def star_file(
    filename: str,
    user=Depends(fastapi_users.get_current_active_user),
    ):
    file_id = await files.exists(filename, user.id)
    if file_id is not None:
        result = await files.starfile(file_id['id'], user.id)
    else:
        return {"error" : "Please check file name submitted."}
    return file_id

@router.patch("/move")
async def move_file_to_folder(
    filename: str,
    parent_folder:str,
    user=Depends(fastapi_users.get_current_active_user),
    ):
    file = await files.exists(filename, user.id)
    if file is not None:
        folder = await folders.exists(parent_folder, user.id)
        if folder is not None:
            await files.move(file["id"],folder["id"])
            return Response(status_code=204)
        else:
            return {"error" : "Please check folder name submitted."}    
    else:
        return {"error" : "Please check file name submitted."}

@router.get("/download")
async def download_file (
    filename: str,
    user=Depends(fastapi_users.get_current_active_user),
    ):
    file_id = await files.exists(filename, user.id)
    if file_id is None:
        return {"error" : "The file does not exist or you do not have required authorization \
        to access it"}
    file_name = await files.get_aws_file_name(file_id['id'])
    response = generate_presigned_url(object_key=file_name["aws_file_name"])

    return {"download_url": response}













# @router.delete("/file")
# async def delete_file ()
