# lessons.py
import json
import os
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, UploadFile, Form
from fastapi import Depends, HTTPException
from fastapi import File
from fastapi import Request
from sqlalchemy import delete, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.api.auth import get_current_user
from src.api.utils.open_ai_audio_process import process_audio
from src.config import settings
from src.database import get_db
from src.middleware.limit import limiter
from src.models import Lesson, Content, User

router = APIRouter(
    tags=["lessons"]
)


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


# CREATE LESSON
@router.post("/api/lessons")
@limiter.limit("50/day")
async def create_lesson(
        request: Request,
        file: UploadFile | None = File(None),
        name: str | None = Form(None),
        uuid: str | None = Form(None),
        id: str | None = Form(None),
        split_text_source: str | None = Form(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not uuid and not id:
        raise HTTPException(status_code=400, detail="No id provided.")

    # Ищем или создаем lesson
    lesson = None
    if id:
        result = await db.execute(select(Lesson).where(Lesson.id == int(id)))
        lesson = result.scalars().first()
    if uuid and lesson is None:
        result = await db.execute(select(Lesson).where(Lesson.uuid == uuid))
        lesson = result.scalars().first()

    # CREATE NEW LESSON
    if lesson is None:
        if not name:
            try:
                name = file.filename.split("/")[-1] if file else "Unnamed Lesson"
            except Exception as e:
                print(f"Ошибка при определении имени: {e}")
                name = "Unnamed Lesson"

        # Создаем новый урок с указанием автора
        lesson = Lesson(
            name=name,
            type="audio",
            uuid=uuid or uuid4(),
            author_id=current_user.id
        )
        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)

    file_split_text = ''

    folder = os.path.join(settings.UPLOAD_DIRECTORY, "files", "lessons", str(lesson.id))

    # CHANGE LESSON ATTRIBUTE
    if not file:
        lesson.name = name
        if uuid:
            lesson.uuid = uuid
        await db.commit()
        await db.refresh(lesson)

        # SAVE NEW SOURCE SPLIT TEXT
        split_text_source_ls = split_text_source.splitlines()
        json_data = {'phrases': split_text_source_ls}
        file_name_relative = os.path.join("files", "lessons", str(lesson.id), 'split_text_source.json')
        file_split_text = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)
        with open(file_split_text, "w", encoding="utf-8") as open_file:
            json.dump(json_data, open_file, ensure_ascii=False, indent=4)

        audio_file_source_full = f'{settings.UPLOAD_DIRECTORY.rstrip("/media/")}{lesson.audio_file_source}'

        audio_file_source_url = lesson.audio_file_source
        audio_file_translate_url = lesson.audio_file_translate

        # SAVE FILE
    if file:
        # Проверка файла
        if not file or '.' not in file.filename:
            raise HTTPException(status_code=400, detail="Invalid file name")

        extension = file.filename.rsplit(".", 1)[-1].lower()
        allowed_extensions = settings.FILE_SETTINGS['audio']['extensions']
        if extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        # Пути сохранения
        audio_file_source_url = f'/media/files/lessons/{lesson.id}/audio_source.{extension}'
        audio_file_source_full = f'{settings.UPLOAD_DIRECTORY.rstrip("/media/")}{audio_file_source_url}'

        audio_file_translate_url = f'/media/files/lessons/{lesson.id}/audio_translate.{extension}'

        os.makedirs(folder, exist_ok=True)
        await save_file(file, audio_file_source_full, settings.FILE_SETTINGS['audio']['max_size'])

    # PROCESS AUDIO
    res = process_audio(audio_file_source_full, lesson.id, file_split_text)
    if not res:
        raise HTTPException(status_code=400, detail="Error processing file")

    # Функции получения данных
    def get_list_files(folder):
        """ Список файлов с сортировкой по числовому значению в имени файла """
        if os.path.exists(folder) and os.path.isdir(folder):
            return sorted(os.listdir(folder), key=lambda x: int(x.split(".")[0]))
        return []

    def get_json_field(file_name, field):
        """ Читаем JSON-файл и получаем нужное поле """
        try:
            with open(file_name, 'r', encoding='utf-8') as open_file:
                return json.load(open_file).get(field, [])
        except Exception:
            return []

    # Получаем файлы
    split_audio_source = get_list_files(f'{folder}/split_audio_source')
    split_audio_translate = get_list_files(f'{folder}/split_audio_translate')
    split_text_source = get_json_field(f'{folder}/split_text_source.json', 'phrases')
    split_text_translate = get_json_field(f'{folder}/split_text_translate.json', 'phrases')

    # split_audio_source = ['0.mp3', '1.mp3', '2.mp3', '3.mp3', '4.mp3']
    # split_text_source = ['Track two.', 'Tell me something about your family.', 'What do you like doing most with your family?', 'Who are you close to in your family?', 'In what way is your family important to you?']

    if len(split_audio_source) != len(split_text_source):
        raise HTTPException(status_code=400, detail="Error len items source")

    if len(split_audio_translate) != len(split_text_translate):
        raise HTTPException(status_code=400, detail="Error len items translate")

    split_data_source = []
    for i, (item_audio, item_text) in enumerate(zip(split_audio_source, split_text_source)):
        line = {}
        line['id'] = i
        line['audio'] = f'/media/files/lessons/{lesson.id}/split_audio_source/{item_audio}'
        line['text'] = item_text
        split_data_source.append(line)

    split_data_translate = []
    for i, (item_audio, item_text) in enumerate(zip(split_audio_translate, split_text_translate)):
        line = {}
        line['id'] = i
        line['audio'] = f'/media/files/lessons/{lesson.id}/split_audio_translate/{item_audio}'
        line['text'] = item_text
        split_data_translate.append(line)

    # Сохраняем в базу
    lesson.split_audio_source = split_audio_source
    lesson.split_audio_translate = split_audio_translate
    lesson.split_text_source = '\n'.join(split_text_source)
    lesson.split_text_translate = '\n'.join(split_text_translate)
    lesson.audio_file_source = audio_file_source_url
    lesson.audio_file_translate = audio_file_translate_url

    lesson.split_data_source = split_data_source
    lesson.split_data_translate = split_data_translate

    await db.commit()
    await db.refresh(lesson)
    return lesson


# Получение всех уроков
@router.get("/api/lessons")
async def get_lessons(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    print(f"Текущий пользователь: {current_user}")

    result = await db.execute(
        select(Lesson).where(Lesson.author_id == current_user.id)
    )
    lessons = result.scalars().all()

    return lessons


# Получение урока по ID
@router.get("/api/lessons/{lesson_id}")
async def get_lesson(
        lesson_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()

    if not lesson:
        raise HTTPException(status_code=404, detail="No content found for the given lesson")

    return lesson


# Получение contents по ID лекции
@router.get("/api/lessons/{lesson_id}/contents")
async def get_lesson_contents_by_id(
        lesson_id: int,
        db: AsyncSession = Depends(get_db)
):
    # Создаем запрос с сортировкой
    query = select(Content).filter_by(lesson_id=lesson_id).order_by(asc(Content.position))
    # Выполняем запрос
    result = await db.execute(query)
    # Получаем все результаты
    contents = result.scalars().all()

    if not contents:
        raise HTTPException(status_code=404, detail="No content found for the given lesson")

    return contents


# Удаление урока по ID
@router.delete("/api/lessons/{lesson_id}")
async def delete_lesson(
        lesson_id: int,
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    await db.execute(delete(Lesson).where(Lesson.id == lesson_id))
    await db.commit()

    return {"data": "success", "error": ""}


# Find lesson by id
async def get_lesson_by_id(
        lesson_id: int,
        db: AsyncSession = Depends(get_db)
) -> Lesson | None:
    lesson_result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = lesson_result.scalars().first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
