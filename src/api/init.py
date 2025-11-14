from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import Content
from src.models import Lesson

router = APIRouter(
    tags=["init"]
)


async def delete_all_data(db: AsyncSession):
    await db.execute(delete(Content))
    await db.commit()

    await db.execute(delete(Lesson))
    await db.commit()


def clear_text(txt):
    txt = txt.replace("\u00A0", "")
    txt.strip()
    return txt


# Маршрут для инициализации данных
@router.post("/api/init")
async def init_data(db: AsyncSession = Depends(get_db)):
    # return {"not use now": True}

    await delete_all_data(db)

    return {"ok": True}
