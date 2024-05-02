from fastapi import FastAPI, File, UploadFile
from typing import List
import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import dotenv_values
import os

app = FastAPI()

# Receive collection name and uploaded PDF, return doc_ids
@app.post("/process_pdf/")
# async def process_pdf(collection_name: str, pdf_file: UploadFile = File(...)):
async def process_pdf(collection_name: str, pdf_file: str):
    # # Save the uploaded PDF temporarily
    # with open(pdf_file.filename, "wb") as buffer:
    #     buffer.write(pdf_file.file.read())

    # Load the document and split it into chunks
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()

    # Split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # Create the open-source embedding function
    # embedding_function = OllamaEmbeddings(model="mistral:instruct")
    embedding_function = OpenAIEmbeddings()

    # Connect to database
    chroma_client = chromadb.PersistentClient(path="./mychroma")

    # Create collection
    chroma_client.get_or_create_collection(name=collection_name)

    # Connect to collection through langchain
    lang_chroma = Chroma(client=chroma_client, collection_name=collection_name, embedding_function=embedding_function)

    # Add documents to collection
    doc_ids = lang_chroma.add_documents(docs)

    return {"doc_ids": doc_ids}

# Delete collection based on collection name
@app.delete("/delete_collection/")
async def delete_collection(collection_name: str):
    # Connect to database
    chroma_client = chromadb.PersistentClient(path="./mychroma")

    # Check that collection exits
    if collection_name not in [c.name for c in chroma_client.list_collections()]:
        return {"message": f"Collection '{collection_name}' does not exist."}
    else:
        # Delete collection
        chroma_client.delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully."}

# Receive collection name and uploaded PDF, return doc_ids
@app.post("/query/")
async def query(query: str):

    # Create the open-source embedding function
    embedding_function = OllamaEmbeddings(model="mistral:instruct")

    # Connect to database
    chroma_client = chromadb.PersistentClient(path="./mychroma")

    # if collection_name not in [c.name for c in chroma_client.list_collections()]:
    #     return {"message": f"Collection '{collection_name}' does not exist."}
    
    # # Create collection
    # chroma_client.get_collection(name=collection_name)

    # Connect to collection through langchain
    lang_chroma = Chroma(client=chroma_client, embedding_function=embedding_function)

    # Add documents to collection
    docs = lang_chroma.similarity_search(query)

    return {"docs": docs}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
