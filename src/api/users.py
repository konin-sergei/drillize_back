# /src/api/users.py
from fastapi import APIRouter, Depends
from fastapi import Request
from passlib.context import CryptContext
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.config import logger
from src.database import get_db
from src.middleware.limit import limiter
from src.models import User
from src.schemas.user import UserOutSchema, UserCreateSchema, EmailConfirmSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["users"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_user(db: AsyncSession, user_data: UserCreateSchema):
    hashed_password = hash_password(user_data.password)
    db_user = User(email=str(user_data.email), hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from src.models import UserEmailConfirm
from src.config import settings


async def save_confirmation_code(db: AsyncSession, email: str, code: str):
    """Сохраняет код подтверждения в таблицу user_email_confirm"""
    try:
        result = await db.execute(select(UserEmailConfirm).filter_by(email=email))
        existing_entry = result.scalars().first()

        if existing_entry:
            existing_entry.code = code
            existing_entry.send_date = datetime.utcnow()
        else:
            confirmation_entry = UserEmailConfirm(
                email=email, code=code, send_date=datetime.utcnow()
            )
            db.add(confirmation_entry)

        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def send_email_for_confirm(db: AsyncSession, client_email: str):
    """Отправка письма с подтверждением email"""
    secret_code = secrets.randbelow(9000) + 1000  # 4-значный код

    # Сохраняем код в базу данных
    await save_confirmation_code(db, client_email, str(secret_code))

    subject = "Email Confirmation - Retolu"

    # Текстовая версия письма (для устройств без HTML)
    text_message = f"""
    Dear user,

    Thank you for registering on Retolu.
    Please enter the confirmation code below to verify your email:

    Confirmation Code: {secret_code}

    If you did not request this, please ignore this email.

    Regards,
    Retolu Team
    """

    # HTML-версия письма (отображается в большинстве почтовых клиентов)
    html_message = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ padding: 20px; background-color: #f4f4f4; border-radius: 8px; }}
            .code {{ font-size: 24px; font-weight: bold; color: #d9534f; }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Email Confirmation</h2>
            <p>Thank you for registering on <strong>Retolu</strong>.</p>
            <p>Please enter the confirmation code below:</p>
            <p class="code">{secret_code}</p>
            <p>If you did not request this, please ignore this email.</p>
            <div class="footer">
                <p>Best regards,<br>Retolu Team</p>
            </div>
        </div>
    </body>
    </html>
    """

    SERVICE_EMAIL_HOST = settings.SERVICE_EMAIL_HOST
    SERVICE_EMAIL_PORT = settings.SERVICE_EMAIL_PORT
    SERVICE_EMAIL_USER = settings.SERVICE_EMAIL_USER
    SERVICE_EMAIL_PASSWORD = settings.SERVICE_EMAIL_PASSWORD

    # Формируем письмо с HTML и текстовой версией
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Retolu <{SERVICE_EMAIL_USER}>"  # Должно совпадать с доменом
    msg["To"] = client_email
    msg["Subject"] = subject
    msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg["MIME-Version"] = "1.0"

    # Добавляем текстовую и HTML версии в письмо
    msg.attach(MIMEText(text_message, "plain"))
    msg.attach(MIMEText(html_message, "html"))

    try:
        logger.info(f"Send email {secret_code} on {client_email}")

        # FOR DEBUG
        if settings.SERVER_TYPE == "prod":
            # Устанавливаем соединение и выполняем аутентификацию
            with smtplib.SMTP_SSL(SERVICE_EMAIL_HOST, SERVICE_EMAIL_PORT) as server:
                server.ehlo()
                server.login(SERVICE_EMAIL_USER, SERVICE_EMAIL_PASSWORD)
                server.sendmail(SERVICE_EMAIL_USER, client_email, msg.as_string())

        logger.info(f"Email sent successfully to {client_email}")

    except smtplib.SMTPException as e:
        logger.error(f"Error send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")


@router.get("/limited-endpoint")
@limiter.limit("3/hour")
async def limited_route(
        request: Request,
        email: str,
        db: AsyncSession = Depends(get_db)
):
    return {"message": "This is a rate-limited endpoint"}


# REGISTER
@router.post("/api/users/register", response_model=UserOutSchema)
@limiter.limit("10/hour")
async def register_user(
        request: Request,
        user_data: UserCreateSchema,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter_by(email=user_data.email))
    db_user = result.scalars().first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = await create_user(db=db, user_data=user_data)

    client_email = str(user_data.email)
    await send_email_for_confirm(db, client_email)

    return UserOutSchema(
        error=None,
        id=db_user.id,
        email=db_user.email,
        confirm_email=db_user.confirm_email
    )


# CONFIRM EMAIL
@router.post("/api/users/confirm_email")
@limiter.limit("10/hour")
async def confirm_email(
        request: Request,
        data: EmailConfirmSchema,
        db: AsyncSession = Depends(get_db)
):
    """
    Подтверждение email пользователя
    """
    try:
        # Проверяем, существует ли запись с данным email
        result = await db.execute(select(UserEmailConfirm).filter_by(email=data.email))
        confirmation_entry = result.scalars().first()

        if not confirmation_entry:
            raise HTTPException(status_code=404, detail="Confirmation entry not found")

        # FOR DEBUG
        if settings.SERVER_TYPE == "dev":
            print('DEBUG VERSION REGISTER')
            confirmation_entry.confirm_date = datetime.utcnow()
            user_result = await db.execute(select(User).filter_by(email=data.email))
            user_result.scalars().first()
            await db.commit()
            return {"detail": "Email successfully confirmed"}

        # Проверяем код
        if confirmation_entry.code != data.code:
            raise HTTPException(status_code=400, detail="Invalid confirmation code")

        # Обновляем запись в `user_email_confirm`
        confirmation_entry.confirm_date = datetime.utcnow()

        # Обновляем статус подтверждения email в таблице пользователей
        user_result = await db.execute(select(User).filter_by(email=data.email))
        user = user_result.scalars().first()

        if user:
            user.confirm_email = True  # Подтверждаем email

        await db.commit()
        return {"detail": "Email successfully confirmed"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# GET USERS
@router.get("/api/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users


# GET USER
@router.get("/api/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).filter_by(id=user_id)  # Используем filter_by для фильтрации по полю
    )
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# DELETE
@router.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Используем filter_by для поиска пользователя
    result = await db.execute(
        select(models.User).filter_by(id=user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Удаляем пользователя
    await db.execute(delete(models.User).where(models.User.id == user_id))
    await db.commit()

    return {"detail": "User deleted"}
