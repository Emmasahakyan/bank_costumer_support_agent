# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools.retriever import create_retriever_tool
load_dotenv()

# Load Chroma DB
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Create retriever tool
retriever_tool = create_retriever_tool(
    retriever,
    name="bank_info",
    description="Search for information about bank credits, deposits and branch locations. Use this for ALL questions."
)

class BankResponse(BaseModel):
    answer: str
    bank: str
    topic: str  # should be one of: credits, deposits, branches

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = PydanticOutputParser(pydantic_object=BankResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an Armenian bank customer support assistant. "
            "You ONLY answer questions about Credits, Deposits, and Branch Locations. "
            "You ONLY use information from the bank_info tool, never use outside knowledge. "
            "Always respond in Armenian language. "
            "Give SHORT and DIRECT answers one or two sentences maximum. "
            "If the question is not about Credits, Deposits or Branches, politely refuse in Armenian. "
            "If the tool returns no relevant information, say you don't have that information in Armenian. "
            "For the topic field use ONLY one of these exact words: credits, deposits, branches. "
            "Wrap the output in this format and provide no other text\n{format_instructions}"
            ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [retriever_tool]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

query = input("What can I help you with? ")
raw_response = agent_executor.invoke({"query": query})

try:
    output = raw_response.get("output")
    if isinstance(output, list):
        text = output[0]["text"]
    else:
        text = output
    structured_response = parser.parse(text)
    print(structured_response)
except Exception as e:
    # If parsing fails, just print the raw output
    print(raw_response.get("output"))