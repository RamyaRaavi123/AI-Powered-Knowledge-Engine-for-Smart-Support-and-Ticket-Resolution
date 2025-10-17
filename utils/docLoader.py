
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader,PyPDFLoader


def find_files(path:Path)->list[Path]:
    if path.is_file():
        return [path]
    exts={".txt",".md",".pdf"}
    return [p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in exts]

def load_document(paths: list[Path])->list[Document]:
    docs:list[Document]=[]
    for p in paths:
        try:
            if p.suffix.lower() in ['.txt','.md']:
                docs.extend(TextLoader(str(p),'utf-8').load())
            elif p.suffix.lower() ==".pdf":
                docs.extend(PyPDFLoader(str(p)).load())
        except Exception as e:
            print(f"[WARN] Failed to load document,{e}",)
    return docs
