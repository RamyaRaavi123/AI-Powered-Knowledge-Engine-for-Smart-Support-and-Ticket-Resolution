# import os,sys
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


# CHAT_MODEL=os.environ.get("CHAT_MODEL") or sys.exit('Unable to load CHAT_MODEL from local Environment')
# TEMPERATURE=os.environ.get("CHAT_MODEL_TEMPERATURE") or sys.exit('Unable to load TEMPERATURE from local Environment')

# # def make_rag_chain(retriver):
# #     prompt=ChatPromptTemplate.from_messages(
# #         [
# #             (
# #                 "system",
# #                 "You are a concise, careful assistant. Answer ONLY from the provided context."
# #                 "If the answer is not in context, say you don't know. "
# #                 "Cite sources by filename and, if present, page."
# #              ),
# #              ("human","Question:\n{input}\n\nContext:\n{context}"),
# #         ]
# #     )

# #     # llm=ChatGoogleGenerativeAI(model=CHAT_MODEL,temperature=TEMPERATURE)
# #     llm = HuggingFaceHub(
# #         repo_id=CHAT_MODEL,
# #         huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
# #         model_kwargs={
# #             "temperature": float(TEMPERATURE),
# #             "max_new_tokens": 512,
# #         },
# #     )
# #     doc_chain=create_stuff_documents_chain(llm,prompt)
# #     rag_chain=create_retrieval_chain(retriver,doc_chain)

# #     return rag_chain
# def make_rag_chain(retriever):
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "You are a concise, careful assistant. Answer ONLY from the provided context."
#                 "If the answer is not in context, say you don't know. "
#                 "Cite sources by filename and, if present, page."
#             ),
#             ("human", "Question:\n{input}\n\nContext:\n{context}"),
#         ]
#     )

#     # Define the endpoint
#     llm_endpoint = HuggingFaceEndpoint(
#         repo_id=CHAT_MODEL,
#         huggingfacehub_api_token=os.environ["HuggingFaceHUB_API_TOKEN"],
#         temperature=float(TEMPERATURE),
#         max_new_tokens=512,
#     )

#     # **KEY FIX**: Wrap the endpoint in ChatHuggingFace for the RAG chain
#     chat_model = ChatHuggingFace(llm=llm_endpoint)

#     doc_chain = create_stuff_documents_chain(chat_model, prompt) # <-- Use the chat model
#     rag_chain = create_retrieval_chain(retriever, doc_chain)

#     return rag_chain


import os, sys
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_groq import ChatGroq  # <-- Use Groq instead

CHAT_MODEL = os.environ.get("CHAT_MODEL") or sys.exit('Unable to load CHAT_MODEL from local Environment')
TEMPERATURE = os.environ.get("CHAT_MODEL_TEMPERATURE") or sys.exit('Unable to load TEMPERATURE from local Environment')

def make_rag_chain(retriever):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a concise, careful assistant. Answer ONLY from the provided context. "
                "If the answer is not in context, say you don't know. "
                "Cite sources by filename and, if present, page."
            ),
            ("human", "Question:\n{input}\n\nContext:\n{context}"),
        ]
    )

    # ✅ Use Groq instead of HuggingFace
    chat_model = ChatGroq(
        model=CHAT_MODEL,              # e.g. "llama-3.1-8b-instant"
        temperature=float(TEMPERATURE),
        max_tokens=512
    )

    doc_chain = create_stuff_documents_chain(chat_model, prompt)
    rag_chain = create_retrieval_chain(retriever, doc_chain)

    return rag_chain
