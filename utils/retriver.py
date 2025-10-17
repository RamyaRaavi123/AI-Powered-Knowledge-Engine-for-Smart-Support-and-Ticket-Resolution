import os,sys
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

load_dotenv()

SEARCH_TYPE=os.environ.get("SEARCH_TYPE") or sys.exit('Unable to load SEARCH_TYPE from local Environment')
TOP_K=os.environ.get("TOP_K") or sys.exit('Unable to load TOP_K from local Environment')

def build_retriver(vectorstore :FAISS):
    return vectorstore.as_retriever(
        search_type=SEARCH_TYPE,
        search_kwargs={"k":int(TOP_K)}
        )