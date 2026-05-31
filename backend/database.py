import json, os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_PATH = os.path.join(os.path.dirname(__file__), "art_design.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    userName = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False, default="123456")
    avatar = Column(String(500), default="")
    status = Column(String(2), default="1")
    userGender = Column(String(10), default="男")
    nickName = Column(String(50), default="")
    userPhone = Column(String(20), default="")
    userEmail = Column(String(100), default="")
    createTime = Column(String(20), default="")
    updateTime = Column(String(20), default="")
    roles = relationship("Role", secondary="user_role", back_populates="users")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    roleName = Column(String(50), nullable=False)
    roleCode = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), default="")
    enabled = Column(Boolean, default=True)
    createTime = Column(String(20), default="")
    users = relationship("User", secondary="user_role", back_populates="roles")
    menu_resources = relationship("RoleMenuResource", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_role"
    id = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey("users.id"))
    roleId = Column(Integer, ForeignKey("roles.id"))


class MenuResource(Base):
    __tablename__ = "menu_resources"
    id = Column(Integer, primary_key=True)
    parentId = Column(Integer, ForeignKey("menu_resources.id"), nullable=True)
    name = Column(String(100), nullable=False)
    path = Column(String(200), default="")
    component = Column(String(200), default="")
    meta = Column(Text, default="{}")
    sort = Column(Integer, default=0)
    isFirstLevel = Column(Boolean, default=False)
    children_rel = relationship("MenuResource", backref="parent_rel",
                                 remote_side=[id], order_by="MenuResource.sort")


class RoleMenuResource(Base):
    __tablename__ = "role_menu_resources"
    id = Column(Integer, primary_key=True)
    roleId = Column(Integer, ForeignKey("roles.id"))
    menuResourceId = Column(Integer, ForeignKey("menu_resources.id"))
    authMarks = Column(Text, default="[]")
    role = relationship("Role", back_populates="menu_resources")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contactName = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    status = Column(String(2), default="1")
    address = Column(Text, default="")
    remark = Column(Text, default="")
    createdAt = Column(String(20), default="")
    updatedAt = Column(String(20), default="")


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
