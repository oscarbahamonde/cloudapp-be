from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from api.controller import uploadObject
from api.auth import get_current_user
from api.schemas import User, Contact, Meta, Media
from api.db import create_document, read_document, update_document, delete_document, list_documents, list_documents_by_index, create_index_by_field
from typing import List

AWS_BUCKET = "cdn.oscarbahamonde.cloud"

r = APIRouter()

@r.post("/media", response_model=Media)
async def upload_media(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    """
    Creates a new media object.
    """
    if user.uid is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    media = Media(
        uid=user.uid,
        filename=file.filename,
        content_type=file.content_type,
        size=file.size
    )
    meta = await create_document(media)
    id = meta.id
    media.url = uploadObject(uid=user.uid, id=id, file=file)
    media_meta = await update_document(model=media, id=id)
    media.meta = media_meta
    create_index_by_field(field="uid", col="medias")
    return media

@r.get("/media", response_model=List[Media])
async def list_all_media():
    """
    Lists all media objects.
    """
    medias = await list_documents(col="medias")
    return medias

@r.get("/media/{uid}", response_model=List[Media])
async def list_media_by_uid(uid: str):
    """
    Lists all media objects by uid.
    """
    medias = await list_documents_by_index(col="medias", index="medias_by_uid", value=uid)
    return medias

@r.get("/media/{uid}/{id}", response_model=Media)
async def get_media_by_uid_id(uid: str, id: str):
    """
    Gets a media object by uid and id.
    """
    media = await read_document(col="medias", id=id)
    return media

@r.delete("/media/{uid}/{id}", response_model=Media, dependencies=[Depends(get_current_user)])
async def delete_media_by_uid_id(uid: str, id: str, user: User = Depends(get_current_user)):
    """
    Deletes a media object by uid and id.
    """
    if user.uid is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    media = await read_document(col="medias", id=id)
    if media.uid != user.uid:
        raise HTTPException(status_code=401, detail="Not authorized")
    media_meta = await delete_document(col="medias", id=id)
    media.meta = media_meta
    return media

