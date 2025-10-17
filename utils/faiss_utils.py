import os,sys,dotenv,time
from pathlib import Path
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_PATH=Path(os.environ.get("INDEX_PATH"))or sys.exit('Unable to load INDEX_PATH from local Environment')
EMBED_MODEL=os.environ.get("EMBED_MODEL") or sys.exit('Unable to load EMBED_MODEL from local Environment')

def build_or_load_faiss(chunks:list[Document],rebuild:bool=False,batch_size=10):
    embeddings=GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
    # embeddings=HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    if rebuild:
        print("Building FAISS index from docs ....")
        vs=None
        for i in range(0,len(chunks),batch_size):
            batch=chunks[i:i+batch_size]
            print(f"  Embedding batch {i//batch_size + 1}/{-(-len(chunks)//batch_size)} (size={len(batch)})...")
            if vs is None:
                vs=FAISS.from_documents(batch,embeddings)
            else:
                vs.add_documents(batch)
            time.sleep(40)
        # vs=FAISS.from_documents(chunks,embeddings)
        INDEX_PATH.mkdir(parents=True,exist_ok=True)
        vs.save_local(str(INDEX_PATH))
        print(f"Index Saved to {INDEX_PATH.resolve()}")
    else:
        print("Loading FAISS index from docs....")
        vs=FAISS.load_local(str(INDEX_PATH),embeddings=embeddings,allow_dangerous_deserialization=True)
        print("loaded FAISS index.")
    return vs
