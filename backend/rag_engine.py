from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
import os

CHROMA_DIR = "./chromadb"
os.makedirs(CHROMA_DIR, exist_ok=True)

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))

def add_pdfs_from_dir(pdf_dir):
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_dir, file))
            pages = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(pages)
            vectorstore.add_documents(chunks)
    vectorstore.persist()

def get_rag_chain(system_prompt):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": system_prompt}
    )
    return qa_chain