from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os,sys

load_dotenv()

CHUNK_SIZE=int(os.environ.get("CHUNK_SIZE")) or sys.exit('Unable to load Chunk Size from local Environment')
CHUNK_OVERLAP=int(os.environ.get("CHUNK_OVERLAP"))or sys.exit('Unable to load Chunk Overlap from local Environment')

def split_documents(docs:list[Document],chunk_size:int=CHUNK_SIZE,chunk_overlap:int=CHUNK_OVERLAP):
    splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)