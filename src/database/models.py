from sqlalchemy import Column, Integer, String, func, Table, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

# from sqlalchemy.sql.sqltypes import DateTime  #---?
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

user_m2m_contact = Table(
    "user_m2m_contact",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users_info.id", ondelete="CASCADE")),
    Column("contact_id", Integer, ForeignKey("contacts.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users_info"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    day_of_born = Column(Date, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String(350), nullable=False)
    description = Column(String(250), nullable=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(
        "created_at", DateTime, default=func.now()
    )
    updated_at = Column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    confirmed = Column(
        Boolean, default=False
    )


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    created_at = Column(
        "created_at", DateTime, default=func.now()
    )
    updated_at = Column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    user_id = Column("user_id", ForeignKey("users_info.id", ondelete="CASCADE"))
    user = relationship("User", backref="contacts")