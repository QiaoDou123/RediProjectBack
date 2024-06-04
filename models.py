from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    bill_lists = relationship("BillList", back_populates="owner")

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bill_list_id = Column(Integer, ForeignKey("bill_lists.id"))
    bill_list = relationship("BillList", back_populates="participants")

class BillList(Base):
    __tablename__ = "bill_lists"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="bill_lists")
    items = relationship("Item", back_populates="bill_list")
    participants = relationship("Participant", back_populates="bill_list")
    transactions = relationship("Transaction", back_populates="bill_list")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String, index=True)
    bill_list_id = Column(Integer, ForeignKey("bill_lists.id"))
    bill_list = relationship("BillList", back_populates="items")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)  # Use Float for numeric amount
    whatfor = Column(String)
    payer = Column(String)
    split_between = Column(String)
    bill_list_id = Column(Integer, ForeignKey("bill_lists.id"))
    bill_list = relationship("BillList", back_populates="transactions")
