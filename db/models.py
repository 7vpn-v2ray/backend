from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column

from .engine import Base


class User(Base):
    __tablename__ = "users"

    password: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(unique=True)

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)

class Admin(Base):
    __tablename__ = "admin"

    password: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(unique=True)
    two_fa_status: Mapped[bool] = mapped_column(unique=True,default=False)
    two_fa_key: Mapped[str] = mapped_column(unique=True,default=None)

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)