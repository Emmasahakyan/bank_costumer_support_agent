from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os


documents = []

for bank_name in os.listdir("data"):
    for topic_file in os.listdir(f"data/{bank_name}"):
        topic = topic_file.replace(".txt", "")
        file_path = f"data/{bank_name}/{topic_file}"
        
        print(f"Loading {bank_name} - {topic}...")
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        
        # Add metadata to each document
        for doc in docs:
            doc.metadata = {
                "bank": bank_name,
                "topic": topic
            }
        
        documents.extend(docs)

print(f"Total documents loaded: {len(documents)}")

# Step 3 - Split into chunks
print("Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)
print(f"Total chunks: {len(chunks)}")

# Step 4 - Create embeddings and save to Chroma
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Creating Chroma DB...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Chroma DB saved successfully!")