import streamlit as st
import os
from io import BytesIO
import docx2txt
import tempfile
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GooglePalmEmbeddings
from typing import Optional
from langchain.docstore.document import Document
from streamlit import warning
import numpy as np
import faiss
import hashlib

EMBEDDINGS_DIR = "embeddings"
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
    ".txt": TextLoader,
}


class StudyMaterialProcessor:
    def __init__(self, embedding_model="text-embedding-gecko-001"):
        self.embedding_model = embedding_model
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=50,
        )
        self.embeddings = GooglePalmEmbeddings(
            model=self.embedding_model,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def process_uploaded_files(self, uploaded_files: List, chatbot_id: str, embedding_id: str) -> None:
        """Processes files, creates embeddings, and builds the FAISS index."""
        all_docs = []
        all_embeddings = []

        for uploaded_file in uploaded_files:
            try:
                file_extension = "." + uploaded_file.name.split(".")[-1]
                loader_class = LOADERS.get(file_extension)
                if loader_class:
                    # Use BytesIO to create a file-like object
                    pdf_file = BytesIO(uploaded_file.read())
                    
                    # Write BytesIO to temporary file
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(pdf_file.getvalue())
                        temp_file_path = temp_file.name
                        loader = loader_class(temp_file_path)  # Pass the file path to the loader
                        documents = loader.load()

                    for doc in documents:
                        chunks = self.chunk_text(doc.page_content)
                        for i, chunk in enumerate(chunks):
                            chunked_doc = Document(
                                page_content=chunk,
                                metadata={
                                    "source": uploaded_file.name,
                                    "chunk_id": i
                                }
                            )
                            all_docs.append(chunked_doc)
                            embedding = self.embeddings.embed_query(chunk) 
                            all_embeddings.append(embedding)
                else:
                    print(f"Unsupported file type: {uploaded_file.name}")
            except Exception as e:
                print(f"Error processing file: {uploaded_file.name}. Error: {e}")

        # Create and Save FAISS Index 
        if all_docs and all_embeddings:
            faiss_index = FAISS.from_embeddings(
                [(doc.page_content, embedding) for doc, embedding in zip(all_docs, all_embeddings)],
                self.embeddings
            )
            self.save_faiss_index(faiss_index, embedding_id) 
            self.save_document_store(all_docs, chatbot_id)

    def extract_text_from_file(self, uploaded_file) -> Optional[List[Document]]:
        """Extracts text from different file types."""
        try:
            file_extension = "." + uploaded_file.name.split(".")[-1]
            loader_class = LOADERS.get(file_extension)
            if loader_class:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(uploaded_file.read())
                    loader = loader_class(temp_file_path)
                    data = loader.load()
                    
                    if data:
                        return data
                    else:
                        warning(
                            f"The uploaded file '{uploaded_file.name}' appears to be empty or corrupted. Please check the file and try again."
                        )
            else:
                warning(f"Unsupported file type: {uploaded_file.name}")
        except Exception as e:
            warning(f"An error occurred while processing '{uploaded_file.name}': {e}")
        return None    

    def chunk_text(self, text, chunk_size=1000, chunk_overlap=50):
        """Breaks down text into smaller chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return splitter.split_text(text)

    def save_faiss_index(self, index: FAISS, embedding_id: str) -> None:
        """Saves the FAISS index to a file."""
        index_path = os.path.join(EMBEDDINGS_DIR, f"index_{embedding_id}.faiss")
        faiss.write_index(index.index, index_path)

    def load_faiss_index(self, embedding_id: str, chatbot_id: str) -> Optional[FAISS]:  
        """Loads the FAISS index from the file."""
        index_path = os.path.join(EMBEDDINGS_DIR, f"index_{embedding_id}.faiss")
        if os.path.exists(index_path):
            try:
                loaded_index = faiss.read_index(index_path)
                document_store = self.load_document_store(chatbot_id) 
                if document_store is not None:
                    return FAISS(
                        embedding_function=self.embeddings,
                        index=loaded_index,
                        docstore=document_store,
                        index_to_docstore_id=list(range(len(document_store)))
                    )
                else:
                    print(f"Error: Could not load document store for chatbot_id {chatbot_id}")
                    return None
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
        return None

    def save_document_store(self, document_store: List[Document], chatbot_id: str) -> None:
        """Saves the document store for the chatbot."""
        docs_dir = os.path.join("uploads", chatbot_id, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        for i, doc in enumerate(document_store):
            file_path = os.path.join(docs_dir, f"doc_{i}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(doc.page_content)

    def load_document_store(self, chatbot_id: str) -> Optional[List[Document]]:
        """Loads the document store for the specified chatbot."""
        docs_dir = os.path.join("uploads", chatbot_id, "docs") 
        document_store = []
        if os.path.exists(docs_dir):
            for filename in os.listdir(docs_dir):
                file_path = os.path.join(docs_dir, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        document_store.append(Document(page_content=f.read()))
        return document_store

    def get_relevant_text(self, query: str, embedding_id: str, chatbot_id: str, top_k: int = 3) -> str:
        """Retrieves relevant text from the chatbot's FAISS index."""
        faiss_index = self.load_faiss_index(embedding_id, chatbot_id)
        print("FAISS Index Loaded:", faiss_index)  # Debug: Is the index loaded correctly?
        if faiss_index:
            docs_and_scores = faiss_index.similarity_search_with_score(query, k=top_k)
            print("Docs and Scores:", docs_and_scores)  # Debug: Inspect search results
            relevant_text = ""
            for doc, score in docs_and_scores:
                print("Doc Index:", docs_and_scores.index((doc, score))) # Debug: Check index
                relevant_text += (
                    f"**Document (Score: {score:.4f}, Source: {doc.metadata.get('source', 'N/A')}):**\n"
                    f"{doc.page_content}\n\n"
                )
            return relevant_text
        else:
            return "No documents have been processed for this embedding yet."