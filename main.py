import json
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools.retriever import create_retriever_tool
from stt import listen
from tts import speak
load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

retriever_tool = create_retriever_tool(
    retriever,
    name="bank_info",
    description="Search for information about bank credits, deposits and branch locations. Use this for ALL questions."
)

class BankResponse(BaseModel):
    answer: str
    bank: str
    topic: str

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
parser = PydanticOutputParser(pydantic_object=BankResponse)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an Armenian bank customer support assistant. "
        "You ONLY answer questions about Credits, Deposits, and Branch Locations. "
        "You ONLY use information from the bank_info tool, never use outside knowledge. "
        "Always respond in Armenian language with a COMPLETE SENTENCE. "
        "Example answer: 'Ֆաստ Բանկի ավանդի տոկոսադրույքը կազմում է 8-10.5%' "
        "For bank field use ONLY one of: IDBank, Fastbank, Ameriabank. "
        "For topic field use ONLY one of: credits, deposits, branches. "
        "If the question is not about Credits, Deposits or Branches, politely refuse in Armenian. "
        "Wrap the output in this format and provide no other text\n{format_instructions}"
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions=parser.get_format_instructions())

tools = [retriever_tool]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=3
)

print("Listening for your question..")
query = listen()

if query is None:
    print("Could not understand. Please try again.")
else:
    try:
        raw_response = agent_executor.invoke({"query": query})
        output = raw_response.get("output")
        if isinstance(output, list):
            text = output[0]["text"]
        else:
            text = output
        if '"properties"' in text:
            data = json.loads(text)
            text = json.dumps(data["properties"])
        structured_response = parser.parse(text)
        print(f"\n{structured_response.answer}\n")
        speak(structured_response.answer)
    except Exception as e:
        # Get the raw output
        output = raw_response.get("output")
        if isinstance(output, list):
            text = output[0]["text"]
        else:
            text = output
        # Print the actual refusal message from LLM
        print(f"\n{text}\n")
        speak(text)
