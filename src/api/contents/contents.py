# contents.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import Content

router = APIRouter(
    tags=["contents"]
)


# Получение всех контентов
@router.get("/api/contents/")
async def get_contents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Content).order_by(asc(Content.position)))
    contents = result.scalars().all()
    return contents


# Получение контента по ID
@router.get("/api/contents/{content_id}")
async def get_content(content_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Content).filter_by(id=content_id))
    content = result.scalars().first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return content


# Удаление контента по ID
@router.delete("/api/contents/{content_id}")
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Content).filter_by(id=content_id))
    content = result.scalars().first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    await db.execute(delete(Content).where(Content.id == content_id))
    await db.commit()

    return {"detail": "Content deleted", "id": content_id}
