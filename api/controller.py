from boto3 import client
from botocore.exceptions import ClientError
from pydantic import HttpUrl, EmailStr
from fastapi import UploadFile, File
from api.config import env

def initClient(service:str):
    try:
        ServiceClient = client(service, region_name=env.get('aws_region_name'),
                    aws_access_key_id=env.get('aws_access_key_id'),
                    aws_secret_access_key=env.get('aws_secret_access_key')) 
        return ServiceClient
    except ClientError as e:
        print(e)
        return None

s3 = initClient('s3')
cognito = initClient('cognito-idp')
ses = initClient('ses')

def sendEmail(name:str, email:EmailStr, message:str):
    try:
        response = ses.send_email(
            Source="dev@oscarbahamonde.cloud",
            Destination={
                'ToAddresses': ["dev@oscarbahamonde.cloud"]
            },
            Message={
                'Subject': {
                    'Data': f"Email from {name}<{email}>"
                },
                'Body': {
                    'Text': {
                        'Data': message
                    }
                }
            })
        return response
    except ClientError as e:
        print(e)
        return None
    
    
def uploadObject(uid:str, id:str, file:UploadFile = File(...)) -> HttpUrl:
    try:
        response = s3.upload_fileobj(
            fileobj=file.file,
            Bucket='www.smartpro.cloud',
            Key=f"{uid}/{id}/{file.filename}",
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        return response['Location']
    except ClientError as e:
        print(e)
        return None

