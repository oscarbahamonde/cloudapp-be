from dotenv import load_dotenv
from os import getenv, environ
from fastapi import File, UploadFile
from typing import List, Dict, Optional, Callable
from api.schemas import User, Contact, Media
from api.db import create_document
from starlette.responses import JSONResponse

environ.clear()
load_dotenv()

from pydantic import BaseModel
from typing import List, Dict, Optional

from boto3 import Session

session = Session(
    aws_access_key_id=getenv("aws_access_key_id"),
    aws_secret_access_key=getenv("aws_secret_access_key"),
    region_name=getenv("aws_region_name")
)
    
cli: Callable = session.client
rsc: Callable = session.resource

"""
    Available AWS resources:
    - cloudformation
    - cloudwatch
    - dynamodb
    - ec2
    - glacier
    - iam
    - opsworks
    - s3
    - sns
    - sqs
"""

AWS_BUCKET = "cdn.oscarbahamonde.cloud"

s3 = cli("s3")

# res = s3.create_bucket(Bucket="cdn.oscarbahamonde.cloud")

#res = s3.put_object(
#    Bucket=AWS_BUCKET,
#    Key="/html/index.html",
#    Body=open("index.html", "rb")
#)

res = s3.delete_object(
    Bucket=AWS_BUCKET,
    Key="/html/index.html"
)

print(res)