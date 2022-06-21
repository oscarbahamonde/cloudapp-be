from dotenv import load_dotenv
from os import environ
environ.clear()
load_dotenv()
from api.schemas import Meta
from faunadb.client import FaunaClient
from typing import Dict, List
from datetime import datetime

fql = FaunaClient(secret=environ['fauna_secret']).query

from faunadb import query as q
from pydantic import BaseModel
from faunadb.objects import FaunaTime

def collection_exists(col:str)->bool:
    return fql(q.exists(q.collection(col)))

def create_collection(col:str):
    if not collection_exists(col):
        return fql(q.create_collection({
            "name": col
        }))

def create_document(model:BaseModel)->Meta:
    collection_name = f"{model.__class__.__name__.lower()}s"
    create_collection(collection_name)
    response = fql(q.create(q.collection(collection_name), {
        "data": model.dict()
    }))
    ts = response['ts']
    id = response['ref'].id()
    ts_int_part = str(ts)[:10]
    ts_decimal_part = str(ts)[11:]
    representation = ts_int_part + "." + ts_decimal_part
    updated_at = datetime.fromtimestamp(float(representation)).strftime("%Y-%m-%d %H:%M:%S")
    return Meta(id=id, ts=ts, updated_at=updated_at)

def read_document(id:str, col:str)->Dict:
    response = fql(q.get(q.ref(q.collection(col), id)))['data']
    return response


def update_document(id:str, model:BaseModel, col:str)->Meta:
    response = fql(q.update(q.ref(q.collection(col), id), {
        "data": model.dict()
    }))
    ts = response['ts']
    id = response['ref'].id()
    ts_int_part = str(ts)[:10]
    ts_decimal_part = str(ts)[11:]
    representation = ts_int_part + "." + ts_decimal_part
    updated_at = datetime.fromtimestamp(float(representation)).strftime("%Y-%m-%d %H:%M:%S")
    return Meta(id=id, ts=ts, updated_at=updated_at)

def delete_document(id:str, col:str)->Meta:
    response = fql(q.delete(q.ref(q.collection(col), id)))
    ts = response['ts']
    id = response['ref'].id()
    ts_int_part = str(ts)[:10]
    ts_decimal_part = str(ts)[11:]
    representation = ts_int_part + "." + ts_decimal_part
    updated_at = datetime.fromtimestamp(float(representation)).strftime("%Y-%m-%d %H:%M:%S")
    return Meta(id=id, ts=ts, updated_at=updated_at)

def list_documents(col:str)->List[Dict]:
    response = fql(q.map(q.lambda_("data"), q.collection(col)))
    return response

def list_documents_by_index(col:str, index:str, value:str)->List[Dict]:
    response = fql(q.map(q.lambda_("data"), q.index(index, value, q.collection(col))))
    return response

def index_exists(index:str)->bool:
    return fql(q.exists(q.index(index)))

def create_index_by_field(field:str, col:str):
    index_name = f"{col}_by_{field}"
    if not index_exists(index_name):
        try:
            fql(q.create_index({
                "data": q.index(index_name, field, q.collection(col))
            }))
        except Exception as e:
            print(e)
        finally:
            return index_name