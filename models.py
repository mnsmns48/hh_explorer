from sqlalchemy import DateTime, func, BIGINT, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Модели таблиц БД

class Base(DeclarativeBase):
    pass


class HHBase(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)  # Номер выдачи
    scrape_date: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())  # Дата парсинга
    schedule: Mapped[str | None]  # График
    experience: Mapped[str | None]  # Опыт
    job_title: Mapped[str]  # Должность
    url: Mapped[str]  # Ссылка
    salary_from: Mapped[int | None] = mapped_column(BIGINT)  # Зарплата от
    salary_to: Mapped[int | None] = mapped_column(BIGINT)  # Зарплата до
    currency: Mapped[str | None]  # Валюта
    skills = mapped_column(ARRAY(Text))  # Навыки


class Resumes(HHBase):
    __tablename__ = 'resume_table'
    gender: Mapped[str | None]  # Пол
    education: Mapped[str | None]  # Образование
    age: Mapped[int | None]  # Возраст
    experience_number: Mapped[float | None]  # Опыт в годах
    status: Mapped[str | None]  # Статус поиска работы
    relevance_date: Mapped[DateTime] = mapped_column(DateTime(timezone=False))  # Дата обновления резюме
    prev_empl_place: Mapped[str | None]  # Прошлое место работы(компания)
    prev_empl_period: Mapped[str | None]  # Прошлое место работы(период)
    prev_empl_duration: Mapped[float | None]  # Прошлое место работы(Продолжительность работы)
    prev_empl_job_title: Mapped[str | None]  # Прошлое место работы(Должность)
    city: Mapped[str | None]  # Город
    business_trip_ready: Mapped[str | None]  # Готовность к командировкам
    languages: Mapped[str | None]  # Языки
    university: Mapped[str | None]  # ВУЗ


class Vacancies(HHBase):
    __tablename__ = 'vacancy_table'
    company_title: Mapped[str | None]  # Название компании
    publication_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))  # Дата публикации
    text: Mapped[str | None] = mapped_column(Text)  # Текст вакансии
    # rank: Mapped[float | None]  # Рейтинг компании
    # recommend: Mapped[int | None]  # Рекомендуют работодателя


class AreasMain(DeclarativeBase):
    __abstract__ = True


class Areas(AreasMain):
    __tablename__ = 'areas'
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    parent_id: Mapped[int | None]
    name: Mapped[str | None]
