from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import SQLDatabaseLoader
from sqlalchemy import create_engine

# Database Connection (update DB_URL as needed)
DB_URL = "sqlite:///books_chroma_db.db"
engine = create_engine(DB_URL)

# Load documents from the database (modify the SQL query based on your schema)
loader = SQLDatabaseLoader(engine, "SELECT * FROM books")
docs = loader.load()

# Create embeddings and store the documents in Chroma
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()


def query_retriever(query: str):
    """
    Given a query, retrieve relevant documents from the vector store.
    """
    relevant_docs = retriever.get_relevant_documents(query)
    return relevant_docs


# Example usage
if __name__ == "__main__":
    query = "What are the key takeaways from book X?"
    retrieved_docs = query_retriever(query)

    for idx, doc in enumerate(retrieved_docs, start=1):
        print(f"Document {idx}:")
        print("Metadata:", doc.metadata)
        print("Content:", doc.page_content)
        print("-" * 40)
