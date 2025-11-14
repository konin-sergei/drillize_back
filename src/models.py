# src/models.py


from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, ARRAY, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base


class UserEmailConfirm(Base):
    __tablename__ = "user_email_confirm"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    send_date = Column(DateTime, default=None, nullable=True)
    code = Column(String(50), nullable=True)
    confirm_date = Column(DateTime, default=None, nullable=True)

    def __str__(self):
        return self.id




# Пользователи
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False, nullable=True)
    confirm_email = Column(Boolean, default=False, nullable=True)

    lessons = relationship("Lesson", back_populates="author")

    def __str__(self):
        return f"User(id={self.id}, email={self.email})"


class Lesson(Base):
    __tablename__ = "lesson"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("lesson.id"), nullable=True)
    type = Column(String(20), nullable=False)

    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    author = relationship("User", back_populates="lessons")

    audio_file_source = Column(String(255), nullable=True)
    audio_file_translate = Column(String(255), nullable=True)

    text_source = Column(Text, nullable=True)
    text_translate = Column(Text, nullable=True)

    split_text_source = Column(Text, nullable=True)
    split_text_translate = Column(Text, nullable=True)



    split_audio_source = Column(ARRAY(String), nullable=True)
    split_audio_translate = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    draft = Column(Boolean, default=True, nullable=True)
    uuid = Column(UUID(as_uuid=True), default=None, unique=True, nullable=True)

    split_data_source = Column(JSON, nullable=True)
    split_data_translate = Column(JSON, nullable=True)


    # Отношение с самим собой (родительский урок)
    parent = relationship(
        "Lesson",
        remote_side="Lesson.id",
        backref="children",
        cascade="all, delete"
    )

    def __str__(self):
        return f"Lesson(id={self.id}, name={self.name}, author_id={self.author_id})"




# Контенты
class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)
    field = Column(String(20), nullable=True)  # main_audio, part_audio, auto_script, translate, real_script
    lesson_id = Column(Integer, ForeignKey("lesson.id"), nullable=False)
    position = Column(Integer, nullable=True)
    url = Column(String(255), nullable=True)
    file = Column(String(255), nullable=True)
    text_source = Column(Text, nullable=True)

    split_text_source = Column(Text, nullable=True)
    split_text_translate = Column(Text, nullable=True)

    split_audio_source = Column(ARRAY(String), nullable=True)
    split_audio_translate = Column(ARRAY(String), nullable=True)

    poster = Column(String(255), nullable=True)
    thumbnails = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    # Связь с уроком
    lesson = relationship("Lesson", backref="content_set", cascade="all, delete")

    def __str__(self):
        return f'{self.id}'

