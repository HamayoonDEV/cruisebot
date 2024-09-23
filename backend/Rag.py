from flask import Flask, request, jsonify
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import Document
from langchain_qdrant import QdrantVectorStore
from groq import Groq
from dotenv import load_dotenv
import ollama
import os
from flask_cors import CORS
# Load environment variables
load_dotenv()

# Load the Groq API key and Qdrant details from environment variables
groq_api_key = os.getenv('GROQ_API_KEY')
qdrant_url = os.getenv('QDRANT_URL')
qdrant_key = os.getenv('QDRANT_API_KEY')
collection_name = os.getenv('QDRANT_COLLECTION_NAME')

#Groq Api initilization
client = Groq(
    api_key=os.environ.get(groq_api_key),
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Initialize vector_store to None
vector_store = None

def load_data():
    global vector_store  # Use global to modify the variable

    # URLs where model gets the data
    urls = [
        "https://www.cruise.com/cruise-deals/royal-caribbean-cruise-deals/",
        "https://www.cruise.com/cruise-deals/celebrity-cruise-deals/",
        "https://www.cruise.com/cruise-deals/princess-cruise-deals/",
        "https://www.cruise.com/cruise-deals/holland-america-cruise-deals/",
        "https://www.cruise.com/cruise-deals/norwegian-cruise-deals/",
        "https://www.cruise.com/cruise-deals/cunard-cruise-deals/",
        "https://www.cruisedirect.com/cruise-line/carnival-cruise-line",
        "https://www.cruisedirect.com/cruise-line/celebrity-cruises",
        "https://www.cruisedirect.com/cruise-line/costa-cruises",
        "https://www.cruisedirect.com/cruise-line/cunard",
        "https://www.cruisedirect.com/cruise-line/disney-cruise-line",
        "https://www.cruisedirect.com/cruise-line/holland-america",
        "https://www.cruisedirect.com/cruise-line/msc-cruises",
        "https://www.cruisedirect.com/cruise-line/norwegian-cruise-line",
        "https://www.cruisedirect.com/cruise-line/princess-cruises",
        "https://www.cruisedirect.com/cruise-line/royal-caribbean",
        "https://www.cruisedirect.com/cruise-line/virgin-voyages"
    ]

    # Load data
    all_docs = []
    for url in urls:
        loader = WebBaseLoader(url)
        docs = loader.load()
        all_docs.extend(docs)

    # Split the pages into smaller text chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Number of characters per chunk
        chunk_overlap=200  # Overlap between chunks
    )

    # Assuming chunk_list contains Document objects
    chunk_list = [text_splitter.split_text(chunk.page_content) for chunk in all_docs]

    text_list = []
    for a in chunk_list:
        for chunk in a:
            doc_string = Document(page_content=chunk)
            text_list.append(doc_string)

    # Embed the chunks using Hugging Face Embeddings
    embd_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    vector_store = QdrantVectorStore.from_documents(
        text_list,
        embd_model,
        url=qdrant_url,
        api_key=qdrant_key,
        collection_name=collection_name,
        force_recreate=True
    )


def get_response(query):
    # Step 1: Retrieve the relevant chunks based on the query
    docs = vector_store.similarity_search(query, k=4)  # Adjust k as needed

    # Step 2: Combine the retrieved chunks
    retrieved_text = " ".join([doc.page_content for doc in docs])

    #Groq model implitation
    response= client.chat.completions.create(
  messages=[
        {
            "role": "user",
            "content": "Educate customers like a salesperson, using clear sections and bullet points for easy readability."
        },
        {
            "role": "Assistant",
            "content": retrieved_text,
        }
    ],
    model="llama3-8b-8192",
)

    #Step 3: Use Hugging Face model to generate a response based on the retrieved text
    # response = ollama.chat(model="llama3.1",   messages=[
    #     {
    #         "role": "user",
    #         "content": "Educate customers like a salesperson, Use simple bullet points like this: - Point one - Point two"
    #     },
    #     {
    #         "role": "Assistant",
    #         "content": retrieved_text,
    #     }
    # ])
   
    #retrun from Groq model
    return response.choices[0].message.content if response else "There is no search!"

    #retrun from ollama model with out structured data.
    #return response['message']['content'] if response else "there is no search!"

   

load_data()

@app.route('/get_response', methods=['POST'])
def response_endpoint():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Query not provided."}), 400

    if vector_store is None:
        return jsonify({"error": "Vector store not initialized. Please load data first."}), 400

    response = get_response(query)
    return jsonify({"response": response}), 200

if __name__ == "__main__":
    app.run(debug=True)
