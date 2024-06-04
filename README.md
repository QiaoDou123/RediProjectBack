Bill Splitting API
Overview
This FastAPI-based application is designed to help users manage and split bills among participants. The application allows users to create bill lists, add participants, record transactions, and calculate balances to ensure fair splitting of costs.

Features
	User Registration and Retrieval
	Creation of Bill Lists
	Adding Participants to Bill Lists
	Adding and Updating Transactions
	Calculating Balances among Participants
	Deleting Transactions and Bill Lists

Requirements
Python 3.7+
FastAPI
SQLAlchemy
pydantic
passlib
SQLite (default database)

Installation
1.	Clone the repository:
git clone <repository_url>
cd <repository_directory>

2.	Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3.	Install the required dependencies:
pip install -r requirements.txt

Running the Application
1.	Start the FastAPI application:
uvicorn main:app --reload
The application will be available at http://127.0.0.1:8000.
API Endpoints
	User Endpoints
	Create User
	POST /users/
	Request Body:
{"username": "string",
  		"password": "string"}
	Response:
{"id": 1,
"username": "string"}

	Get Users

	GET /users/
	Response:
[
  {
    "id": 1,
    "username": "string"
  }
]
	Bill List Endpoints
	Create Bill List
	POST /bill_lists/
	Request Body:
{
  "title": "string",
  "participants": [
    {
      "name": "string"
    }
  ]
}
	Response:
{
  "id": 1,
  "title": "string",
  "participants": [
    {
      "name": "string"
    }
  ],
  "transactions": []
}
	Get Bill Lists
	GET /bill_lists/
	Response:
[
  {
    "id": 1,
    "title": "string",
    "participants": [
      {
        "name": "string"
      }
    ],
    "transactions": []
  }
]
	Get Bill List by ID
	GET /bill_lists/{bill_list_id}
	Response:
{
  "id": 1,
  "title": "string",
  "participants": [
    {
      "name": "string"
    }
  ],
  "transactions": []
}
	Delete Bill List
	DELETE /bill_lists/{bill_list_id}
	Response:
{
  "detail": "Bill list deleted successfully"
}

	Transaction Endpoints
	Create Transaction
	POST /bill_lists/{bill_list_id}/transactions/
	Request Body:
{
  "amount": 0.0,
  "whatfor": "string",
  "payer": "string",
  "split_between": "string"
}
	Response:
{
  "id": 1,
  "amount": 0.0,
  "whatfor": "string",
  "payer": "string",
  "split_between": "string",
  "bill_list_id": 1
}
	Update Transaction
	PATCH
 /bill_lists/{bill_list_id}/transactions/{transaction_id}
	Request Body:
{
  "amount": 0.0,
  "whatfor": "string",
  "payer": "string",
  "split_between": "string"
}
	Response:
{
  "id": 1,
  "amount": 0.0,
  "whatfor": "string",
  "payer": "string",
  "split_between": "string",
  "bill_list_id": 1
}
	Delete Transaction
	DELETE /bill_lists/{bill_list_id}/transactions/{transaction_id}
	Response:
{
  "detail": "Transaction deleted successfully"
}
	Balance Calculation Endpoint
	Calculate Balance
	GET /bill_lists/{bill_list_id}/balance
	Response:
{
  "participant1": {
    "participant2": 0.0
  }
}
Database
The application uses SQLite as the default database. The database file (bill.db) will be created in the project directory. The database schema is defined using SQLAlchemy models.

Note
The provided code has a commented-out section that drops all data in the database. Be careful when using Base.metadata.drop_all(bind=engine) as it will delete all tables and their data.
