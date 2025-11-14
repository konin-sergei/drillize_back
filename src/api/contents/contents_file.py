# /src/api/contents/contents_file.py
import json
import os
from typing import List, Optional

import aiofiles
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.utils.open_ai_audio_process import process_audio
from src.config import settings
from src.database import get_db
from src.models import Content

router = APIRouter(
    tags=["contents_file"]
)


async def get_or_create_content(
        content_id: Optional[int],
        content_type: str,
        content_field: str,
        lesson_id: int,
        db: AsyncSession
) -> Content:
    """
    Создание или обновление объекта Content.
    """

    result = await db.execute(select(Content).filter_by(lesson_id=lesson_id, field=content_field))
    content = result.scalars().first()
    if content is None:
        content = Content(
            type=content_type,
            field=content_field,
            lesson_id=lesson_id
        )
        db.add(content)
        await db.commit()
        await db.refresh(content)

    # if content_id is not None:
    #     result = await db.execute(select(Content).filter_by(lesson_id=lesson_id, field=content_field))
    #     content = result.scalars().first()
    #     if content is None:
    #         raise HTTPException(status_code=404, detail="Content not found")
    # else:
    #     max_position_stmt = select(func.coalesce(func.max(Content.position), 0)).where(Content.lesson_id == lesson_id)
    #     result = await db.execute(max_position_stmt)
    #     max_position = result.scalar()
    #     new_position = max_position + 1
    #
    #     content = Content(
    #         type=content_type,
    #         field=content_field,
    #         lesson_id=lesson_id,
    #         position=new_position
    #     )
    #     db.add(content)
    #     await db.commit()
    #     await db.refresh(content)

    return content


async def save_file(file: UploadFile, file_path: str, max_size: int):
    """
    Сохранение загружаемого файла асинхронно с проверкой размера.
    """
    file_size = 0
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # Читаем по 1 МБ
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > max_size:
                    raise HTTPException(status_code=400, detail="File too large.")
                await buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        await file.close()


def get_image_size(filename: str):
    image = Image.open(filename)
    width, height = image.size
    return width, height


async def create_content_file(

        lesson_id: int,
        content_id: Optional[int],
        file: UploadFile,
        content_type: str,
        content_field: str,
        allowed_extensions: List[str],
        allowed_max_size: int,
        db: AsyncSession
) -> Content:
    """
    Универсальная функция для загрузки файлов или сохранения текстовых данных.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = file.filename
    if not filename or '.' not in filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Создание или обновление объекта Content
    content = await get_or_create_content(content_id, content_type, content_field, lesson_id, db)

    # Формирование пути для сохранения файла
    relative_file_path = os.path.join("files", "lessons", str(lesson_id), f'{content_field}.{extension}')
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, relative_file_path)
    print('file_path', file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Сохранение файла
    await save_file(file, file_path, allowed_max_size)

    # Формирование URL-пути к файлу
    content.file = f"/media/{relative_file_path}"

    if content_type == 'image':
        width, height = get_image_size(file_path)
        content.width = width
        content.height = height

    await db.commit()
    await db.refresh(content)

    return content
    # return {
    #     "id": content.id,
    #     "type": content.type,
    #     "field": content.field,
    #     "filename": filename,
    #     "file_url": content.file,
    #     "width": content.width,
    #     "height": content.height,
    # }


# Когда известен content_id
@router.put("/api/contents/{content_id}/upload_file")
async def upload_file(
        lesson_id: int,
        content_id: Optional[int],
        content_type: str,
        field: str,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    if content_type not in settings.FILE_SETTINGS:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    extensions = settings.FILE_SETTINGS[content_type]['extensions']
    max_size = settings.FILE_SETTINGS[content_type]['max_size']

    return await create_content_file(
        lesson_id=lesson_id,
        content_id=content_id,
        file=file,
        content_type=content_type,
        field=field,
        allowed_extensions=extensions,
        allowed_max_size=max_size,
        db=db
    )


@router.post("/api/contents/add_file")
async def add_file(
        lesson_id: int,
        content_type: str,
        content_field: str,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    exit(0)
    """
    Загрузка нового файла без указания content_id.
    """
    if content_type not in settings.FILE_SETTINGS:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    extensions = settings.FILE_SETTINGS[content_type]['extensions']
    max_size = settings.FILE_SETTINGS[content_type]['max_size']

    content = await create_content_file(
        lesson_id=lesson_id,
        content_id=None,  # Для создания нового контента
        file=file,
        content_type=content_type,
        content_field=content_field,
        allowed_extensions=extensions,
        allowed_max_size=max_size,
        db=db
    )

    file_url = content.file.lstrip("/media/")
    file_audio = os.path.join(settings.UPLOAD_DIRECTORY, file_url)

    res = process_audio(file_audio, 5)

    if res:
        split_audio_source = []
        split_audio_translate = []
        split_text_source = []
        split_text_translate = []

        folder_relative = os.path.join("files", "lessons", str(lesson_id), "split_audio_source")
        folder = os.path.join(settings.UPLOAD_DIRECTORY, folder_relative)
        if os.path.exists(folder) and os.path.isdir(folder):
            split_audio_source = os.listdir(folder)

        folder_relative = os.path.join("files", "lessons", str(lesson_id), "split_audio_translate")
        folder = os.path.join(settings.UPLOAD_DIRECTORY, folder_relative)
        if os.path.exists(folder) and os.path.isdir(folder):
            split_audio_translate = os.listdir(folder)

        file_relative = os.path.join("files", "lessons", str(lesson_id), "split_text_source.json")
        file_split_text = os.path.join(settings.UPLOAD_DIRECTORY, file_relative)
        with open(file_split_text, 'r') as file:
            data_split_text = json.load(file)
            split_text_source = data_split_text['phrases']

        file_relative = os.path.join("files", "lessons", str(lesson_id), "split_text_translate.json")
        file_split_text = os.path.join(settings.UPLOAD_DIRECTORY, file_relative)
        with open(file_split_text, 'r') as file:
            data_split_text = json.load(file)
            split_text_translate = data_split_text['phrases']

    # result = await db.execute(select(Content).filter_by(content_id=content.id))
    # content_db = result.scalars().first()

    content.split_text_source = '\n'.join(split_text_source)
    content.split_text_translate = '\n'.join(split_text_translate)

    content.split_audio_source = split_audio_source
    content.split_audio_translate = split_audio_translate

    await db.commit()
    await db.refresh(content)

    return content
