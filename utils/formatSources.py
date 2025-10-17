from langchain.docstore.document import Document
from pathlib import Path

def format_sources(ctx:list[Document])->str:
    lines=[]
    for d in ctx:
        src=d.metadata.get("source") or d.metadata.get("file_path") or "unknown"
        page=d.metadata.get("page")
        name=Path(src).name
        lines.append(f"{name}"+(f"(page {page})" if page is not None else ""))

    return "\n".join(lines)