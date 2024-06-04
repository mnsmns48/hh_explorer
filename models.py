from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class HHBase(DeclarativeBase):
    __abstract__ = True


class Resume(HHBase):
    __tablename__ = 'resume_table'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    title: Mapped[str]
    link: Mapped[str]
    age: Mapped[str | None]
    excpirience: Mapped[str | None]
    salary: Mapped[str | None]
    status: Mapped[str | None]
    prev_employment: Mapped[str | None]


