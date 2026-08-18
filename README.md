# AI Customer Support with JWT Authentication

An AI-powered customer support platform built using **FastAPI, LangChain, LangGraph, SQL Server, and Streamlit** that enables users to securely authenticate, interact with an AI assistant, and retrieve customer-related information through natural language queries.

The application implements **JWT-based authentication** to ensure secure access to protected APIs. Users can register, log in, and receive access tokens that are required to interact with the AI support system. Passwords are securely stored using **Argon2 hashing**.

The AI assistant leverages **LangChain and LangGraph** to orchestrate workflows, manage conversation state, and invoke tools for retrieving customer and order information from a SQL Server database. The system can answer customer queries, check order status, provide account information, and handle support requests through a conversational interface.

## Key Features

* User Registration and Login
* JWT Token-Based Authentication and Authorization
* Secure Password Hashing with Argon2
* AI-Powered Customer Support Chatbot
* LangGraph Workflow Management
* Database Integration with SQL Server
* FastAPI REST APIs
* Streamlit-Based User Interface
* Tool Calling for Order and Customer Data Retrieval
* Conversation Memory and Context Management
* Error Handling and Input Validation

## Technology Stack

* **Backend:** FastAPI
* **Authentication:** JWT (JSON Web Token)
* **Password Security:** Argon2
* **AI Framework:** LangChain, LangGraph
* **Database:** Microsoft SQL Server
* **ORM/Database Access:** SQLAlchemy, PyODBC
* **Frontend:** Streamlit
* **Programming Language:** Python

## Project Workflow

1. User registers and creates an account.
2. Password is hashed and stored securely in SQL Server.
3. User logs in and receives a JWT access token.
4. Authenticated requests are validated using JWT.
5. User submits support queries through the Streamlit interface.
6. LangGraph routes the query and invokes appropriate tools.
7. Data is retrieved from SQL Server when required.
8. The AI assistant generates contextual responses and returns them to the user.

This project demonstrates full-stack AI application development by combining secure authentication, REST APIs, database integration, workflow orchestration, and large language model capabilities into a production-oriented customer support solution.
