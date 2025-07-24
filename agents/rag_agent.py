# agents/rag_agent.py
import logging
logger = logging.getLogger(__name__)

from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI

import os

def load_documents():
    folder = "knowledge"
    filenames = ["compliance.txt", "compliance_handbook.txt", "sec_policy.txt"]
    docs = []

    for name in filenames:
        full_path = os.path.join(folder, name)
        if not os.path.exists(full_path):
            raise RuntimeError(f"Missing knowledge file: {full_path}")
        loader = TextLoader(full_path, encoding='utf-8')
        docs.extend(loader.load())
    
    return docs

# Build once at module level (optional for reuse)
documents = load_documents()
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len, separator="\n\n")
chunks = splitter.split_documents(documents)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(chunks, embedding_model)
retriever = vector_store.as_retriever(search_type="similarity", k=3)
rag_chain = RetrievalQA.from_chain_type(llm=OpenAI(), retriever=retriever)

async def query_rag(input_text: str) -> str:
    try:
        retrieved_docs = retriever.get_relevant_documents(input_text)
        trimmed_docs = retrieved_docs[:3]
        logger.info(f"Retrieved chunks: {[doc.page_content[:100] for doc in retrieved_docs]}")
        
        response = rag_chain.invoke({"query": input_text, "context": trimmed_docs})
        if not response:
            return "I'm sorry, but I couldn't find an answer in the compliance knowledge base."
        return response
    except Exception as e:
        logger.error(f"RAG agent failed: {str(e)}")
        return "There was an error retrieving information from the compliance document. Please try again later or rephrase your query."