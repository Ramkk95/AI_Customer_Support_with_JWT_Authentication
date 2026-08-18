from typing import TypedDict

import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import add_messages, StateGraph
from typing import TypedDict, Annotated

from langgraph.prebuilt import ToolNode, tools_condition
from sqlalchemy import text, create_engine
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')


@tool
def rag_help(question: str):
    '''Answer customer questions related to company policies and guidelines.

Use this tool for questions about:
- Return and refund policies
- Order cancellation policies
- Shipping and delivery policies
- Payment policies
- Warranty policies
- Exchange policies
- Customer support guidelines
- Other general company rules and policies

Do not use this tool to check the status or details of a specific order.
For order-specific information, use the order_status tool.

Args:
    question: The customer's question about a company policy.

Returns:
    An answer based on the company's policy documents.
'''
    loader = PyPDFLoader(r'F:\desktop\python-proj\customer_care\customer_care_service_knowledge_base.pdf')

    @st.cache_data
    def db_Data():
        docss = loader.load()
        # text1= '\n'.join(doc.page_content for doc in docs)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(docss)
        embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        text2 = [chunk.page_content for chunk in chunks]
        # vector2 = embedding.embed_documents(text2)
        db = FAISS.from_texts(
            text2,
            embedding)
        return db

    bd = db_Data()
    llm = init_chat_model("gpt-4o")
    results = bd.similarity_search(
        question,
        k=3
    )

    context = '\n\n'.join(result.page_content for result in results)
    message = ChatPromptTemplate.from_messages([
        ('system', '1. Your are a AI Assistance, Your Name is Riya,greet user with your name'
                   '2. donot answer yourself'
                   '3. if not found answer from pdf , say sorry')
        , ('human', f'user question: {question}'
                    f'PDF context: {context}')])

    chain = message | llm | StrOutputParser()
    response = chain.invoke({'question': question})

    return [response]


@tool
def order_manage(order_id: int, work: str):
    """
       Check the status of a specific customer order using the order ID.

       Use this tool for order-specific questions such as:
       - Where is my order?
       - What is the status of my order?
       - Has my order been shipped?
       - Has my order been delivered?
       - Is my order cancelled or pending?
       - cancel my order
       -want to cancel order

       Do not use this tool for general company policy questions.
       """

    @st.cache_resource
    def connection():
        server = "DESKTOP-HSTTJ5C"
        database = "tt2"

        engine = create_engine(
            f"mssql+pyodbc://@{server}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
            "&trusted_connection=yes"
        )
        return engine

    eng = connection()
    if work == 'status':
        with eng.connect() as conn:
            q = """select * from book_detail where order_id =:order_id"""
            resp = conn.execute(text(q), {'order_id': order_id})
            rest = resp.fetchone()
        if rest:
            return ({'order_id': rest[0],
                     'order_name': rest[1],
                     'order_location': rest[2],
                     'order_status': rest[3]})

        else:
            return f'{order_id} location not found'

    if work == 'cancel':
        with eng.connect() as conn:
            q = """select * from book_detail where order_id =:order_id"""
            resp = conn.execute(text(q), {'order_id': order_id})
            rest = resp.fetchone()
        if rest[3] == 'processing':
            with eng.connect() as cnnn:
                q2 = """UPDATE book_detail SET dispatch_status='cancelled' where order_id=:order_id"""
                resp3 = cnnn.execute(text(q2), {'order_id': order_id})
                cnnn.commit()
            return "Order cancelled"

        else:
            return (f"{order_id} can not be cancelled ", {'order_id': rest[0],
                                                          'order_name': rest[1],
                                                          'order_location': rest[2],
                                                          'order_status': rest[3]})

tools = [rag_help, order_manage]
memory = MemorySaver()

config = {'configurable': {'thread_id': '1'}}


class State(TypedDict):
    messages: Annotated[list[str], add_messages]


llm = init_chat_model(
    'gpt-4o')

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    mes = llm_with_tools.invoke(state['messages'])
    return {'messages': [mes]}


build = StateGraph(State)
build.add_node('chatbot', chatbot)
build.add_node('tools', ToolNode(tools))
build.add_edge(START, 'chatbot')
build.add_conditional_edges('chatbot', tools_condition)
build.add_edge('tools', 'chatbot')
graph = build.compile(checkpointer=memory)
