from flask import Flask, request, jsonify
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import TextLoader
from langchain.vectorstores.pgvector import DistanceStrategy
import os
import openai

app = Flask(__name__)

# Get the existing credentials from the environment.
CONNECTION_STRING = os.getenv(
    "PGVECTOR_CONNECTION"
)  # This connection string specifies the PostgreSQL database connection.
embeddings = OpenAIEmbeddings()


@app.route("/add", methods=["POST"])
def add_document():
    data = request.json
    collection_name = data["collection_name"]
    document_path = data["document_path"]

    loader = TextLoader(document_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    db = PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=collection_name,
        connection_string=CONNECTION_STRING,
    )

    return jsonify(
        {
            "message": f"Document {document_path} has been 'read', vectorized by the LLM, and stored in the vector storage"
        }
    )


@app.route("/query", methods=["POST"])
def query():
    data = request.json
    collection_name = data["collection_name"]
    query_text = data["query"]

    db = PGVector(
        collection_name=collection_name,
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
        distance_strategy=DistanceStrategy.COSINE,
    )

    docs_with_score = db.similarity_search_with_score(query_text, k=3)

    # Combine the content of the top 3 documents into a single context string
    context = " ".join([doc.page_content for doc, _ in docs_with_score])

    completion = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Question: {query_text}\n Found Answer: {context} Please answer the question.",
            },
        ],
    )

    return jsonify({"answer": completion.choices[0].message.content})


@app.route("/sql", methods=["POST"])
def get_sql():
    data = request.json
    collection_name = data["collection_name"]
    query_text = data["query"]

    query_embedded = embeddings.embed_query(query_text)
    sql = f"SELECT document, (embedding <=> '{query_embedded}') as cosine_distance FROM {collection_name} ORDER BY cosine_distance LIMIT 3;"

    return jsonify({"sql_query": sql})
