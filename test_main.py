import unittest
from fastapi.testclient import TestClient
from main import app
from database import get_db, engine, SessionLocal
from models import Base
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey,Float
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from typing import List, Optional, Dict
from datetime import date

# Override the database connection for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bill.db"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency override for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAPI(unittest.TestCase):

    def setUp(self):
        # Initialize the test database
        self.db = TestingSessionLocal()
        Base.metadata.create_all(bind=engine)
    
    def tearDown(self):
        # Drop the test database
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def test_create_user(self):
        response = client.post("/users/", json={"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertIn("username", response.json())
        self.assertEqual(response.json()["username"], "testuser")

    def test_create_user_duplicate_username(self):
        client.post("/users/", json={"username": "testuser", "password": "testpassword"})
        response = client.post("/users/", json={"username": "testuser", "password": "newpassword"})
        self.assertEqual(response.status_code, 400)

    def test_read_users(self):
        client.post("/users/", json={"username": "testuser1", "password": "testpassword"})
        client.post("/users/", json={"username": "testuser2", "password": "testpassword"})
        response = client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_create_bill_list(self):
        response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertIn("title", response.json())
        self.assertEqual(response.json()["title"], "test bill list")

    def test_create_bill_list_without_participants(self):
        response = client.post("/bill_lists/", json={"title": "test bill list"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertIn("title", response.json())
        self.assertEqual(response.json()["title"], "test bill list")
    
    def test_read_bill_list(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        response = client.get(f"/bill_lists/{bill_list_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertEqual(response.json()["id"], bill_list_id)
    
    def test_read_non_existent_bill_list(self):
        response = client.get("/bill_lists/9999")
        self.assertEqual(response.status_code, 404)

    def test_create_transaction_for_bill_list(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        response = client.post(f"/bill_lists/{bill_list_id}/transactions/", json={"amount": 100.0, "whatfor": "test transaction", "payer": "participant1", "split_between": "participant1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertIn("amount", response.json())
        self.assertEqual(response.json()["amount"], 100.0)

    def test_create_transaction_with_invalid_amount(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        response = client.post(f"/bill_lists/{bill_list_id}/transactions/", json={"amount": "invalid", "whatfor": "test transaction", "payer": "participant1", "split_between": "participant1"})
        self.assertEqual(response.status_code, 422)

    def test_calculate_balance(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}, {"name": "participant2"}]})
        bill_list_id = bill_list_response.json()["id"]
        client.post(f"/bill_lists/{bill_list_id}/transactions/", json={"amount": 100.0, "whatfor": "test transaction", "payer": "participant1", "split_between": "participant1, participant2"})
        response = client.get(f"/bill_lists/{bill_list_id}/balance")
        self.assertEqual(response.status_code, 200)
        self.assertIn("participant1", response.json())
        self.assertIn("participant2", response.json()["participant1"])
        self.assertEqual(response.json()["participant1"]["participant2"], 50.0)
        self.assertEqual(response.json()["participant2"]["participant1"], -50.0)
    
    def test_calculate_balance_no_transactions(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}, {"name": "participant2"}]})
        bill_list_id = bill_list_response.json()["id"]
        response = client.get(f"/bill_lists/{bill_list_id}/balance")
        self.assertEqual(response.status_code, 200)
        self.assertIn("participant1", response.json())
        self.assertEqual(response.json()["participant1"]["participant2"], 0.0)
        self.assertEqual(response.json()["participant2"]["participant1"], 0.0)

    def test_delete_transaction(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        transaction_response = client.post(f"/bill_lists/{bill_list_id}/transactions/", json={"amount": 100.0, "whatfor": "test transaction", "payer": "participant1", "split_between": "participant1"})
        transaction_id = transaction_response.json()["id"]
        response = client.delete(f"/bill_lists/{bill_list_id}/transactions/{transaction_id}")
        self.assertEqual(response.status_code, 204)
    
    def test_delete_non_existent_transaction(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        response = client.delete(f"/bill_lists/{bill_list_id}/transactions/9999")
        self.assertEqual(response.status_code, 404)

    def test_delete_bill_list(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        response = client.delete(f"/bill_lists/{bill_list_id}")
        self.assertEqual(response.status_code, 204)

    def test_delete_non_existent_bill_list(self):
        response = client.delete("/bill_lists/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_transaction(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        transaction_response = client.post(f"/bill_lists/{bill_list_id}/transactions/", json={"amount": 100.0, "whatfor": "test transaction", "payer": "participant1", "split_between": "participant1"})
        transaction_id = transaction_response.json()["id"]
        update_response = client.patch(f"/bill_lists/{bill_list_id}/transactions/{transaction_id}", json={"amount": 150.0, "whatfor": "updated transaction"})
        self.assertEqual(update_response.status_code, 200)
        self.assertIn("amount", update_response.json())
        self.assertEqual(update_response.json()["amount"], 150.0)

    def test_update_non_existent_transaction(self):
        bill_list_response = client.post("/bill_lists/", json={"title": "test bill list", "participants": [{"name": "participant1"}]})
        bill_list_id = bill_list_response.json()["id"]
        update_response = client.patch(f"/bill_lists/{bill_list_id}/transactions/9999", json={"amount": 150.0, "whatfor": "updated transaction"})
        self.assertEqual(update_response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
