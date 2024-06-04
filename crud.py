from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User, BillList, Participant, Transaction
from schemas import UserCreate, BillListCreate, TransactionCreate, TransactionUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_bill_list(db: Session, bill_list: BillListCreate):
    db_bill_list = BillList(title=bill_list.title)
    db.add(db_bill_list)
    db.commit()
    db.refresh(db_bill_list)

    for participant in bill_list.participants:
        db_participant = Participant(name=participant.name, bill_list_id=db_bill_list.id)
        db.add(db_participant)

    db.commit()
    db.refresh(db_bill_list)

    return db_bill_list

def get_bill_list(db: Session, bill_list_id: int):
    return db.query(BillList).filter(BillList.id == bill_list_id).first()

def get_bill_lists(db: Session):
    return db.query(BillList).all()

def create_transaction(db: Session, bill_list_id: int, transaction: TransactionCreate):
    db_transaction = Transaction(**transaction.dict(), bill_list_id=bill_list_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def calculate_balance(db: Session, bill_list_id: int):
    bill_list = db.query(BillList).filter(BillList.id == bill_list_id).first()
    participants = [participant.name for participant in bill_list.participants]
    balance_record = {p: {other: 0.0 for other in participants} for p in participants}

    for transaction in bill_list.transactions:
        if transaction.split_between:
            splitters = transaction.split_between.split(", ")
            amount_per_person = float(transaction.amount) / len(splitters)
            for splitter in splitters:
                if transaction.payer != splitter:
                    balance_record[transaction.payer][splitter] += amount_per_person
                    balance_record[splitter][transaction.payer] -= amount_per_person

    return balance_record

def delete_transaction(db: Session, bill_list_id: int, transaction_id: int):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.bill_list_id == bill_list_id
    ).first()
    if transaction:
        db.delete(transaction)
        db.commit()
        return True
    return False

def delete_bill_list(db: Session, bill_list_id: int):
    bill_list = db.query(BillList).filter(BillList.id == bill_list_id).first()
    if bill_list:
        db.delete(bill_list)
        db.commit()
        return True
    return False

def update_transaction(db: Session, bill_list_id: int, transaction_id: int, transaction_update: TransactionUpdate):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.bill_list_id == bill_list_id).first()
    if transaction:
        transaction_data = transaction_update.dict(exclude_unset=True)
        for key, value in transaction_data.items():
            setattr(transaction, key, value)
        db.commit()
        db.refresh(transaction)
        return transaction
    return None
