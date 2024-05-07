import requests
import os

# Assuming you have the API key and endpoint URL
API_KEY = os.environ.get("SUPABASE_KEY")

# Adding API key to headers
headers = {"API-Key": API_KEY}

# Making the POST request to PDF endpoint
endpoint_add_pdf = "http://127.0.0.1:8100/add_pdf/"
pdf_request_data = {
    "name": "Example PDF",
    "user_ref": "user1317",
    "pdf_url": "ADD-VALID-URL"
}
response = requests.post(endpoint_add_pdf, json=pdf_request_data, headers=headers)

# Checking the response
if response.status_code == 200:
    data = response.json()
    print("Document IDs:", data['ids'])
else:
    print("Failed to add PDF:", response.status_code, response.text)

# Making the POST request to PDF endpoint
endpoint_rag = "http://127.0.0.1:8100/rag/invoke"
inputs = {"input": "How many articles in the SFDR?", "config": {"configurable": {"search_kwargs": {"k":2, "filter": {"user_ref": "0IGyehWc9PNszrvPzaH0Pr7rKqk2"}}}}}
response = requests.post(endpoint_rag, json=inputs, headers=headers)

# Checking the response
if response.status_code == 200:
    data = response.json()
    print("RAG Response:", data)
else:
    print("Failed complete RAG:", response.status_code, response.text)

# Making the POST request to PDF endpoint
endpoint_delete = "http://127.0.0.1:8100/delete_pdf/"
delete_request_data = {
    "user_ref": "user1317",
    "pdf_url": "ADD-VALID-URL"
}
response = requests.delete(endpoint_delete, json=delete_request_data, headers=headers)

# Checking the response
if response.status_code == 200:
    data = response.json()
    print("Deleted Response:", data)
else:
    print("Failed to delete:", response.status_code, response.text)

