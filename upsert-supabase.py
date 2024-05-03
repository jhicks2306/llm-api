import requests
import io
import os
from typing import List

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from supabase.client import Client, create_client

from langchain_community.vectorstores import SupabaseVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

app = FastAPI()

class PDFRequest(BaseModel):
    name: str
    user_ref: str
    pdf_url: str

def download_pdf(url):
    # Make a GET request to download the PDF
    response = requests.get(url)
    print("Content-Type:", response.headers.get('Content-Type'))
    response.raise_for_status()  # Raise an exception for bad responses
    return response.content

# Receive collection name and uploaded PDF, return doc_ids
@app.post("/process_pdf/")
async def process_pdf(pdf_request: PDFRequest):

    # GET pdf_data from Firebase storage
    pdf_url = pdf_request.pdf_url

    # Load the document and split it into chunks
    loader = PyPDFLoader(pdf_url)
    documents = loader.load()

    # Split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    for doc in docs:
        doc.metadata.update({"user_ref": pdf_request.user_ref, "name": pdf_request.name})

    # Create the open-source embedding function
    # embedding_function = OllamaEmbeddings(model="mistral:instruct")
    embedding_function = OpenAIEmbeddings()

    # Connect to database
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)

    # Access vectorstore
    vector_store = SupabaseVectorStore(
        client=supabase,
        embedding=embedding_function,
        table_name="documents",
        query_name="match_documents",
    )

    # Add documents to vectorstore
    doc_ids = vector_store.add_documents(docs)

    return {"ids": doc_ids}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
