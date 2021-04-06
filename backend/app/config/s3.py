import boto3
import requests
from botocore.exceptions import ClientError


def generate_download_url(object_key=None, content_type=None, expiry=None):

    client = boto3.client("s3",
                          region_name="ap-south-1",
                          aws_access_key_id="AKIARLI5GU2HE5S2O6M6",
                          aws_secret_access_key="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",
                          )
    try:
        response = client.generate_presigned_url('get_object',
                                                 Params={'Bucket': 'nathanbucket123',
                                                         'Key': object_key,
                                                         },
                                                 ExpiresIn=expiry)
        return response
    except ClientError as e:
        print(e)


def aws_upload(filename=None, file_content=None, bucket_name=None, object_name=None,
               fields=None, conditions=None, expiration=None):

    # Generate a presigned S3 POST URL
    s3_client = boto3.client("s3",
                             region_name="ap-south-1",
                             aws_access_key_id="AKIARLI5GU2HE5S2O6M6",
                             aws_secret_access_key="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",
                             )
    try:
        resp = s3_client.generate_presigned_post(Bucket="nathanbucket123",
                                                 Key=filename,
                                                 ExpiresIn=expiration)
    except ClientError as e:
        return None

    # The response contains the presigned URL and required fields
    # Extract the URL and other fields from the response
    post_url = resp['url']
    data = resp['fields']
    # Upload the file using requests module
    response = requests.post(url=post_url, data=data,
                             files={'file': file_content})
    return response
