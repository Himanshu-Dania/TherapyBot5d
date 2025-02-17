from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1) Set up your embedding model
embedding_model = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model, model_kwargs={"device": "cuda"}
)

# 2) Load the existing Chroma DB from the local folder
#    Make sure 'persist_directory' matches wherever you originally saved your Chroma DB
vectordb = Chroma(
    persist_directory="books_chroma_db",  # Folder where chroma.sqlite3 etc. are stored
    collection_name="rag_docs",  # Must match the name used when you created/populated the DB
    embedding_function=embeddings,
)

# 3) Create a retriever
retriever = vectordb.as_retriever(search_kwargs={"k": 2})


def query_retriever(query: str):
    """
    Given a query, retrieve relevant documents from the vector store.
    """
    # If you’re using the standard LangChain retriever,
    # use 'retriever.get_relevant_documents(query)'
    relevant_docs = retriever.invoke(query)
    return relevant_docs


# Example usage
if __name__ == "__main__":
    test_query = "How do I go about the loss of someone?"
    docs = query_retriever(test_query)

    if not docs:
        print("No documents retrieved.")
    else:
        print(f"Retrieved {len(docs)} documents.\n")
        for idx, doc in enumerate(docs, start=1):
            print(f"Document {idx}:")
            print("Metadata:", doc.metadata)
            print("Content:", doc.page_content)
            print("-" * 40)
