import os

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models import Content

router = APIRouter(
    tags=["contents_text"]
)

MAX_TEXT_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_content_text(

        lesson_id: int,
        content_field: str,
        text: str,
        db: AsyncSession,
        content_id: int = None,
        content_type: str = 'text',
        allowed_max_size: int = MAX_TEXT_FILE_SIZE
) -> dict:
    """
    Функция для создания или обновления текстового контента.
    Если передан content_id, происходит обновление; иначе создается новый контент.
    """
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    text_bytes = text.encode('utf-8')
    file_size = len(text_bytes)
    if file_size > allowed_max_size:
        raise HTTPException(status_code=400, detail="Text too large.")

    filename = 'rich.txt'

    if content_id:
        # Обновление контента
        content = await db.get(Content, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        if content.type != 'text':
            raise HTTPException(status_code=400, detail="Invalid content type for text update")
    else:
        max_position_stmt = select(func.coalesce(func.max(Content.position), 0)).where(Content.lesson_id == lesson_id)
        result = await db.execute(max_position_stmt)
        max_position = result.scalar()
        new_position = max_position + 1

        # Создание нового контента
        content = Content(
            type=content_type,
            field=content_field,
            lesson_id=lesson_id,
            position=new_position
        )
        db.add(content)
        await db.commit()
        await db.refresh(content)

    # Общий код для записи файла
    relative_file_path = os.path.join(
        "files",
        "lessons",
        str(lesson_id),
        "contents",
        str(content.id),
        filename
    )
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, relative_file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(text_bytes)
    except Exception as e:
        if not content_id:
            await db.delete(content)
            await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to save text: {e}")

    # Если новый контент, добавляем путь к файлу
    if not content_id:
        relative_file_url = relative_file_path.replace(os.path.sep, '/')
        content.file = f"/media/{relative_file_url}"

    # Обновляем текст в базе данных
    content.text = text
    db.add(content)
    await db.commit()
    await db.refresh(content)

    return {
        "id": content.id,
        "type": content.type,
        "text": content.text,
        "file_url": content.file
    }


@router.post("/api/contents/add_text")
async def add_text(
        lesson_id: int,
        content_field: str,
        text: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    res = await save_content_text(
        lesson_id=lesson_id,
        content_field=content_field,
        text=text,
        db=db,
        content_type='text',
        allowed_max_size=MAX_TEXT_FILE_SIZE
    )
    return res


@router.put("/api/contents/{content_id}/update_text")
async def update_text(
        lesson_id: int,
        content_id: int,
        text: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    return await save_content_text(
        lesson_id=lesson_id,
        content_id=content_id,
        text=text,
        db=db,
        allowed_max_size=MAX_TEXT_FILE_SIZE
    )
