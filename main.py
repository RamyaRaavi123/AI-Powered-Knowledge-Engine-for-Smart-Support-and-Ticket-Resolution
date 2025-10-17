import asyncio
import os,sys,time,datetime
from dotenv import load_dotenv
from utils.docLoader import find_files,load_document
from utils.splitter import split_documents
from utils.faiss_utils import build_or_load_faiss
from utils.retriver import build_retriver
from utils.buildRagChain import make_rag_chain
from utils.formatSources import format_sources
from utils.contentRecognizer import categorizationBuilder
from utils.tokenHistoryFinder import isTokenRepeated
from pathlib import Path
from utils.sheets_utils import insertRecord
load_dotenv()

            
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

REBUILD_INDEX = os.environ.get("REBUILD_INDEX", "False")
REBUILD_INDEX = REBUILD_INDEX.lower() in ("true", "1", "yes")
DOC_PATH=Path(os.environ.get("DOCS_PATH") or sys.exit('Unable to load DOC_PATH from local Environment'))
CHUNK_SIZE=Path(os.environ.get("CHUNK_SIZE") or sys.exit('Unable to load CHUNK_SIZE from local Environment'))
CHUNK_OVERLAP=Path(os.environ.get("CHUNK_OVERLAP") or sys.exit('Unable to load CHUNK_OVERLAP from local Environment'))

import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

rag=None
def get_rag():
    global rag
    if rag is None:
        main()
    return rag


def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY is not set")
    chunks=None
    global rag
    if REBUILD_INDEX:
        print(f"Scanning docs under: {DOC_PATH.resolve()}....")
        files=find_files(Path(os.environ.get("DOCS_PATH")))
        if not files:
            raise SystemExit("No .txt/ .md/ .pdf files found")
        print(f"Loading {len(files)} files....")
        docs=load_document(files)
        print(f"Splitting {len(docs)} docs(size={CHUNK_SIZE},overlap={CHUNK_OVERLAP})....")
        chunks=split_documents(docs)

    vectorstore=build_or_load_faiss(chunks,rebuild=REBUILD_INDEX)
    retriever=build_retriver(vectorstore)
    rag=make_rag_chain(retriever)
    

def askQuestion(Question):
    if Question:
        result=rag.invoke({"input":Question})
        answer=result.get("answer") or result.get("output") or str(result)
        print("Answer: \n"+answer.strip())

        ctx=result.get("context",[])
        if ctx:
            print("Sources:")
            print(format_sources(ctx))
        return (answer,format_sources(ctx))


# if __name__=="__main__":
#     main()
#     while(True):
#         Question=input("\nQuestion (To Exit Press 0): ")
#         if Question=="0":
#             break
#         else:
#             categories=["maintainance","product support","refund"]
#             ticket_id = int(time.time())  # or use datetime for better format
#             ticket_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             ticket_content=Question
#             ticket_cat=categorizationBuilder(Question,categories)
#             ticket_by="Balaji"
#             ticket_status="process"
#             isTokenRepeated(Question)
#             insertRecord([ticket_id,ticket_content,ticket_cat,ticket_timestamp,ticket_by,ticket_status])
#             # print(ticket_id)
#             askQuestion(Question)
def system(Question):
    categories = [
    "Getting Started",
    "Troubleshooting",
    "Connectivity",
    "Power Management",
    "Hardware",
    "Support",
    "Software",
    "Security"
    ]
    ticket_id = int(time.time())  
    ticket_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket_content=Question
    ticket_cat=categorizationBuilder(Question,categories)
    ticket_by="Balaji"
    ticket_status="process"
    isTokenRepeated(Question)
    insertRecord([ticket_id,ticket_content,ticket_cat,ticket_timestamp,ticket_by,ticket_status])
    return askQuestion(Question)

