from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

class BillListBase(BaseModel):
    title: str

class BillListCreate(BillListBase):
    participants: List["ParticipantCreate"] = []

class BillListOut(BillListBase):
    id: int
    participants: List["ParticipantOutNoId"] = []
    transactions: List["TransactionOut"] = []

    class Config:
        orm_mode = True

class ParticipantBase(BaseModel):
    name: str

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantOutNoId(ParticipantBase):
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: float  # Use float for numeric amount
    whatfor: str
    payer: str
    split_between: str

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    bill_list_id: int

    class Config:
        orm_mode = True

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, description="The new amount of the transaction")
    whatfor: Optional[str] = Field(None, description="Description of what the transaction was for")
    payer: Optional[str] = Field(None, description="Who paid in this transaction")
    split_between: Optional[str] = Field(None, description="How the transaction amount is split among participants")

class BalanceRecord(BaseModel):
    balance: Dict[str, Dict[str, float]]

    class Config:
        orm_mode = True
