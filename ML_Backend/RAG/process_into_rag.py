import os
import json
import argparse
import torch
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def ingest_text_to_chroma(
    json_file: str, persist_dir: str, collection_name: str = "rag_docs"
):
    """
    Reads text from a JSON file and stores chunked embeddings in a Chroma vector store.

    Args:
        json_file (str): Path to the JSON file containing extracted text.
            The file should have the structure:
            {
                "filename1.pdf": "Some text ...",
                "filename2.epub": "Some other text ...",
                ...
            }
        persist_dir (str): Directory where Chroma data will be persisted.
        collection_name (str): Name of the Chroma collection.
    """

    # 1. Read data from JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Torch device set to: {device}")

    # 2. Initialize embeddings (HuggingFace in this example)
    #    You can replace with OpenAIEmbeddings if you prefer.
    embedding_model = "sentence-transformers/all-mpnet-base-v2"
    print(f"[INFO] Using HuggingFace Embeddings: {embedding_model}")
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model, model_kwargs={"device": device}
    )

    # 3. Create or load an existing Chroma DB
    #    `persist_directory` allows us to save the index to disk.
    print(
        f"[INFO] Initializing Chroma DB at '{persist_dir}' in collection '{collection_name}'."
    )
    vectordb = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    # 4. Create a text splitter to chunk large texts
    #    Adjust chunk_size/chunk_overlap as needed for your use case.
    text_splitter = CharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separator="\n"
    )

    # 5. Ingest each document from JSON
    for doc_name, doc_text in data.items():
        if not doc_text:
            print(f"[WARNING] '{doc_name}' is empty. Skipping.")
            continue

        # Split into chunks
        chunks = text_splitter.split_text(doc_text)
        print(f"[INFO] '{doc_name}' => {len(chunks)} chunks generated.")

        # Prepare metadata for each chunk
        metadatas = [{"source": doc_name} for _ in range(len(chunks))]

        # Add chunks to Chroma
        vectordb.add_texts(chunks, metadatas=metadatas)

    # 6. Persist the database so it can be reused
    vectordb.persist()
    print(f"[INFO] Ingestion complete. Data persisted to '{persist_dir}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest text from a JSON file into a Chroma vector store."
    )
    parser.add_argument("json_file", help="Path to the JSON file with extracted text.")
    parser.add_argument(
        "--persist_dir",
        default="chroma_db",
        help="Directory to store the Chroma database. Defaults to 'chroma_db'.",
    )
    parser.add_argument(
        "--collection_name",
        default="rag_docs",
        help="Name of the Chroma collection. Defaults to 'rag_docs'.",
    )
    args = parser.parse_args()

    ingest_text_to_chroma(args.json_file, args.persist_dir, args.collection_name)


if __name__ == "__main__":
    main()
