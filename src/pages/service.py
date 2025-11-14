# src/pages/site.py

from fastapi import APIRouter
from fastapi import Request, Form, Cookie
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
from fastapi.responses import RedirectResponse

router = APIRouter(
    tags=["HTML service"]
)


from fastapi import Depends, Request


async def get_current_user(request: Request):
    return request.user  # Это будет доступно, если Middleware настроено


@router.get("/lessons")
async def get_dashboard(request: Request, user=Depends(get_current_user)):
    # Пример данных, которые вы хотите передать в шаблон
    user_settings = {
        'profile_image': 'https://example.com/path/to/image.jpg',  # Замените на реальные данные
        'username': 'JohnDoe',  # Пример дополнительных данных
    }

    resolver_match = {'url_name': request.url.path}
    # return templates.TemplateResponse("your_template.html", {"request": request, "current_path": request.url.path})

    user = {'first_name': '', 'second_name': '', 'email': '<EMAIL>'}
    # Передаем данные в шаблон через контекст
    return templates.TemplateResponse(
        'service/lessons.html',
        {
            'request': request,  # Обязательный параметр
            'user': user,  # Ваши данные
            'user_settings': user_settings,  # Дополнительные данные
            'resolver_match': resolver_match,  # Дополнительные данные
        }
    )


@router.get("/add_audio")
async def add_audio(request: Request, user=Depends(get_current_user)):
    print('page add audio')

    return templates.TemplateResponse(
        'service/add_audio.html',
        {
            'request': request,  # Обязательный параметр
        }
    )



@router.get("/add_text")
async def add_text(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        'service/add_text.html',
        {
            'request': request,  # Обязательный параметр
        }
    )

# @router.get("/service/sections/{section_id}")
# async def section_one(request: Request, section_id: int, db: AsyncSession = Depends(get_db), password: str = Cookie(None)):
#     result = await db.execute(select(Lesson).filter_by(section_id=section_id, type='item').order_by(asc(Lesson.id)))
#     lesson = result.scalars().first()
#
#     lesson_code = lesson.code
#     lesson_code = lesson_code.replace('.', '_')
#
#     case_id = 1
#     redirect_url = request.url_for('lesson_theory', section_id=section_id, lesson_code=lesson_code, case_id=case_id, tab='theory')
#
#     return RedirectResponse(url=redirect_url)
#
#
# @router.get("/service/sections/{section_id}/cases/{case_id}/lessons/{lesson_code}/tab/{tab}", name="lesson_theory")
# async def lesson_one(request: Request, section_id: int, case_id: int, lesson_code: str, tab: str, db: AsyncSession = Depends(get_db), password: str = Cookie(None)):
#     # lessons
#     result = await db.execute(select(Lesson).filter_by(section_id=section_id))
#     lessons = result.scalars().all()
#
#     # sections
#     result = await db.execute(select(Section).order_by(asc(Section.position)))
#     sections = result.scalars().all()
#
#     # curren section
#     section_result = await db.execute(select(Section).filter_by(id=section_id))
#     section = section_result.scalars().first()
#
#     # curren lesson
#     lesson_code = lesson_code.replace('_', '.')
#     lesson_result = await db.execute(select(Lesson).filter_by(code=lesson_code, section_id=section_id))
#     lesson = lesson_result.scalars().first()
#     if lesson is None:
#         raise HTTPException(status_code=404, detail="Lesson not found")
#
#     # curren case
#     # todo добавить фильтр id=case_id
#     case_result = await db.execute(select(Case).filter_by(section_id=section_id))
#     case = case_result.scalars().first()
#
#     url = request.url.path.rstrip('/')
#
#     # contents
#     result = await db.execute(select(Content).filter_by(lesson_id=lesson.id).order_by(asc(Content.position)))
#     contents = result.scalars().all()
#
#     if not tab:
#         tab = 'theory'
#     return templates.TemplateResponse(
#         'service/main.html',
#         {
#             'request': request,
#             'lessons': lessons,
#             'sections': sections,
#             'contents': contents,
#             'section': section,
#             'lesson': lesson,
#             'case': case,
#             'url': url,
#             'tab': tab
#         }
#     )
