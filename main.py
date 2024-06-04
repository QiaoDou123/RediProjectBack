from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
import crud
import schemas

from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey,Float
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from typing import List, Optional, Dict
from datetime import date

app = FastAPI()

# API routes
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.get("/users/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip, limit)

@app.post("/bill_lists/", response_model=schemas.BillListOut)
def create_bill_list(bill_list: schemas.BillListCreate, db: Session = Depends(get_db)):
    return crud.create_bill_list(db, bill_list)

@app.get("/bill_lists/{bill_list_id}", response_model=schemas.BillListOut)
def read_bill_list(bill_list_id: int, db: Session = Depends(get_db)):
    bill_list = crud.get_bill_list(db, bill_list_id)
    if bill_list is None:
        raise HTTPException(status_code=404, detail="Bill list not found")
    return bill_list

@app.get("/bill_lists/", response_model=List[schemas.BillListOut])
def read_bill_lists(db: Session = Depends(get_db)):
    return crud.get_bill_lists(db)

@app.post("/bill_lists/{bill_list_id}/transactions/", response_model=schemas.TransactionOut)
def create_transaction_for_bill_list(bill_list_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_transaction(db, bill_list_id, transaction)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

@app.get("/bill_lists/{bill_list_id}/balance", response_model=Dict[str, Dict[str, float]])
def calculate_balance(bill_list_id: int, db: Session = Depends(get_db)):
    bill_list = crud.get_bill_list(db, bill_list_id)
    if bill_list is None:
        raise HTTPException(status_code=404, detail="Bill list not found")
    return crud.calculate_balance(db, bill_list_id)

@app.delete("/bill_lists/{bill_list_id}/transactions/{transaction_id}", status_code=204)
def delete_transaction(bill_list_id: int, transaction_id: int, db: Session = Depends(get_db)):
    if not crud.delete_transaction(db, bill_list_id, transaction_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "Transaction deleted successfully"}

@app.delete("/bill_lists/{bill_list_id}", status_code=204)
def delete_bill_list(bill_list_id: int, db: Session = Depends(get_db)):
    if not crud.delete_bill_list(db, bill_list_id):
        raise HTTPException(status_code=404, detail="Bill list not found")
    return {"detail": "Bill list deleted successfully"}

@app.patch("/bill_lists/{bill_list_id}/transactions/{transaction_id}", response_model=schemas.TransactionOut)
def update_transaction(bill_list_id: int, transaction_id: int, transaction_update: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    transaction = crud.update_transaction(db, bill_list_id, transaction_id, transaction_update)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Add this to your existing FastAPI app instance
router = APIRouter()
router.add_api_route("/bill_lists/{bill_list_id}/transactions/{transaction_id}", update_transaction, methods=["PATCH"])
app.include_router(router)
