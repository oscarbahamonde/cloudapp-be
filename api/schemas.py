from pydantic import (
    BaseModel,
    BaseConfig,
    HttpUrl,
    EmailStr,
    Field,
    validator

)

from datetime import datetime

from typing import (
    List,
    Dict,
    Optional,
    Callable,
    Union
)

from faunadb.objects import (
    Ref,
    Query,
    FaunaTime,
    _Expr
)

from faunadb import query as q

from faunadb.client import FaunaClient

from enum import Enum

from api.config import env

fauna_client : FaunaClient = FaunaClient(
    secret=env.get('fauna_secret')
)

fql: Callable = fauna_client.query

class Meta(BaseModel):
    id: Optional[str]
    ts: Optional[str]
    updated_at: Optional[str]

class Contact(BaseModel):
    name: str
    email: EmailStr
    message: str
    
class User(BaseModel):
    uid: str
    displayName:str
    email:EmailStr
    photoURL:Optional[HttpUrl]
    role:str
    
class UserSchema(User):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        orm_mode = True
        arbitrary_types_allowed: bool = True
    meta: Meta = Field(default=Meta())
    
class Media(BaseModel):
    uid:str
    filename:str
    url:HttpUrl
    content_type:str
    size:Optional[int]

class MediaSchema(Media):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        orm_mode = True
        arbitrary_types_allowed: bool = True
    meta: Meta = Field(default=Meta())
    
class Content(BaseModel):
    uid:str
    title:str
    content:str
    media:Optional[Media]
    tags:List[str]
    
class ContentSchema(Content):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        orm_mode = True
        arbitrary_types_allowed: bool = True
    meta: Meta = Field(default=Meta())
    
class Product(Content):
    price:float
    description:str
    category:Optional[str]
    subcategory:Optional[str]
    brand:Optional[str]
    variants:Optional[List[str]]
    images:Optional[List[Media]]

class ProductSchema(Product):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        orm_mode = True
        arbitrary_types_allowed: bool = True
    meta: Meta = Field(default=Meta())