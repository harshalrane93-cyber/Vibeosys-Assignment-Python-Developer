from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, func, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from typing import Optional
import enum

# Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class CategoryEnum(str, enum.Enum):
    finished = "finished"
    semi_finished = "semi-finished"
    raw = "raw"

class UnitEnum(str, enum.Enum):
    mtr="mtr"; mm="mm"; ltr="ltr"; ml="ml"; cm="cm"; mg="mg"; gm="gm"; unit="unit"; pack="pack"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    category = Column(SQLEnum(CategoryEnum))
    description = Column(String(250))
    product_image = Column(Text)
    sku = Column(String(100))
    unit_of_measure = Column(SQLEnum(UnitEnum))
    lead_time = Column(Integer)
    created_date = Column(TIMESTAMP, server_default=func.now())
    updated_date = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

Base.metadata.create_all(bind=engine)
class ProductCreate(BaseModel):
    name: str
    category: CategoryEnum
    description: str | None = None
    product_image: str | None = None
    sku: str
    unit_of_measure: UnitEnum
    lead_time: int

app = FastAPI()

@app.post("/product/add")
def add_product(data: ProductCreate):
    db = SessionLocal()
    obj = Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    db.close()
    return obj

@app.get("/product/list")
def list_product():
    db = SessionLocal()
    data = db.query(Product).all()
    db.close()
    return data

@app.get("/product/{pid}/info")
def info_product(pid: int):
    db = SessionLocal()
    data = db.query(Product).filter(Product.id==pid).first()
    db.close()
    return data