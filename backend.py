from typing import Annotated
from sqlalchemy import text,create_engine
import requests.exceptions
from sqlalchemy import text
from langchain_core.messages import SystemMessage, HumanMessage
from pwdlib import PasswordHash
from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from connection import connectio_n
from llm import graph,config
from token_gen import create_token, creat_new_user
from pydantic import BaseModel, Field, EmailStr

app=FastAPI()

password_hash= PasswordHash.recommended()



@app.get('/')
def root():
    return {'message':'Hello World'}


class Model(BaseModel):
    password:Annotated[str,Field(min_length=6,max_length=12)]
    email:Annotated[EmailStr,Field(...,description='email address')]
    username:str



@app.post('/register')
def register_user(data:Model):
    engine=connectio_n()
    try:
        with engine.connect() as conn:
            q=''' INSERT INTO log_in2  (username, email, password) VALUES (:username,:email,:password)'''
            dat=data.model_dump()
            password=password_hash.hash(dat['password'])
            res=conn.execute(text(q),{'username':dat['username'],'email':dat['email'],'password':password})
            conn.commit()
        return 'Registered successfully!'
    except SQLAlchemyError as e:
       return e


@app.post('/token')
def login( form_data: OAuth2PasswordRequestForm = Depends()):
    username= form_data.username
    password= form_data.password
    data={'username':username,'password':password}
    engine= connectio_n()
    with engine.connect() as conn:
        q3 = ''' select * from log_in2 where username=:username'''
        resr = conn.execute(text(q3), {'username':username})
        rest = resr.fetchone()
    if username != rest[0]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid username')
    varify_password=password_hash.verify(password,rest[2])
    if varify_password is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid username or password')
    access_token=create_token(
        {
                'sub': username
        }
    )

    return {'access_token':access_token,'token_type':'bearer'}

@app.get('/detail_s')
def get_detail_s(ques:str,current_user:str= Depends(creat_new_user)):

    messages = [SystemMessage(content='You are an AI Customer Care Assistant for an e-commerce company.'

                                      'Your job is to help customers with:'
                                      '1. General customer-care questions'
                                      '2. Order-related questions'
                                      '3. Order status and order details'
                                      '4. Cancel order on user request if it has dispatch_status is  processing'

                                      'You have access to two tools:'

                                      '1. rag_help'
                                      '   - Use this tool for general customer-care information.'
                                      '  - Examples:'
                                      '   - Return policy'
                                      '  - Refund policy'
                                      '- Cancellation policy'
                                      '- Shipping policy'
                                      '- Delivery information'
                                      '- Payment methods'
                                      '- Warranty'
                                      '- Frequently asked questions'
                                      '- If the answer can be found in the customer-care knowledge base, use this tool.'


                                      '2. order_manage'
                                      '  - Use this tool when the customer asks about a specific order.'
                                      ' - Examples:'
                                      '  - "Where is my order?"'
                                      ' - "What is the status of order 12345?"'
                                      '- "Has my order been shipped?"'
                                      '- "When will my order arrive?"'
                                      '- "Show me my order details."'
                                      '- "want to cancel my order"'
                                      '- "cancel my order"'
                                      '- Always use this tool instead of guessing order information.'

                                      'Tool selection rules:'

                                      '- If the question is about company policies, procedures, or general customer support information, use rag_help.'
                                      '- If the question is about a specific order or order ID, use order_manage.'
                                      '- If the question requires both general policy information and specific order information, use both tools when necessary.'
                                      '- Never invent order information.'
                                      '- Never assume an order status.'
                                      '- If an order ID is required but the customer has not provided one, politely ask for the order ID.'
                                      '- Use the information returned by the tools to formulate the final answer.'

                                      'Response rules:'

                                      '- Be polite, concise, and helpful.'
                                      '- Answer directly.'
                                      '- Do not mention internal tools, databases, RAG, SQL, LangChain, or LangGraph to the customer.'
                                      '- Do not expose internal implementation details.'
                                      '- If the available information is insufficient, clearly say what information is needed.'
                                      '- Never make up information that is not provided by the tools.'

                                      'Find order_id from question'

                                      '-question= what is status of 1'
                                      'take order_id=1'
                                      'question= i want to return product 2'
                                      'take order_id=2'
                                      'question: what is return policy'
                                      'order_id=Null'
                                      'question: cancel my order with order_id=1'
                                      'order_id=1'
                                      'question: cancel my order with order_id=1'
                                      'order_id=1'
                                      'question: cancel order 1'
                                      'order_id=1'
                                      'question: cancel order id 2'
                                      'order_id=2'
                              ),
                HumanMessage(content=ques)]
    res=graph.invoke({'messages': messages}, config=config)
    mes=res['messages'][-1].content
    return {'Ai_res':mes}