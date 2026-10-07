# Unit Testing POC - Chat Application

## Overview

This POC demonstrates how I used `pytest` to write and run unit tests for an existing Python Flask Chat Application.

The purpose of this POC is to understand how application functionality can be tested independently without depending on the actual production database.

I used the existing Chat Application for this POC instead of creating a separate application.

## Application Used for Testing

The Chat Application provides APIs to:

- Create users
- Get users
- Send messages between users
- Get the conversation between two users

The application is built using Python, Flask, SQLAlchemy, and PostgreSQL.

## Objective of the POC

The main objective was to understand and demonstrate:

- How to set up `pytest`
- How to write test cases
- How to use assertions
- How to test Flask APIs
- How to test valid and invalid inputs
- How to mock database operations
- How to test exception/error scenarios
- How to check test coverage using `pytest-cov`

## Technologies Used

- Python 3.11
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- SQLAlchemy
- pytest
- pytest-cov
- unittest.mock

## Project Structure

```text
chat_application/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── venv/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md