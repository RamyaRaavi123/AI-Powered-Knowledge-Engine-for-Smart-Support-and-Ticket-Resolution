# from langchain_groq import ChatGroq
# from langchain.chains import LLMChain
# from langchain.prompts import ChatPromptTemplate
# from langchain.agents import load_tools, initialize_agent, AgentType,Tool
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


# from langchain.memory import ConversationBufferMemory
# from main import askQuestion,get_rag
# from dotenv import load_dotenv
# import sys,os

# CHAT_MODEL=os.environ.get("CHAT_MODEL") or sys.exit('Unable to load CHAT_MODEL from local Environment')
# TEMPERATURE=os.environ.get("CHAT_MODEL_TEMPERATURE") or sys.exit('Unable to load TEMPERATURE from local Environment')


# load_dotenv()


# # prompt =ChatPromptTemplate.from_template("You are a helpful Agent. Answer this question clearly :{question}")
# # chain=prompt |llm

# def search_articles(query:str):
#     rag=get_rag()
#     result=rag.invoke({"input":query})
#     answer=result.get("answer") or result.get("output") or str(result)
#     ctx=result.get("context")
#     articles=[doc.metadata.get("source","Unknown") for doc in ctx[:5]]
#     return f"{answer} \nTop articles :\n"+"\n".join(articles)

# # tools = load_tools(['wikipedia'],llm=llm)
# # def buildAgent():
# #     # llm = ChatGroq(model=os.environ.get("AGENT_MODEL"))
# #     llm = HuggingFaceHub(
# #         repo_id=CHAT_MODEL,
# #         huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
# #         model_kwargs={
# #             "temperature": float(TEMPERATURE),
# #             "max_new_tokens": 512,
# #         },
# #     )
# #     tools=[
# #         Tool(
# #             name="HP_KB_Search",
# #             func=search_articles,
# #             description="Searches the internal HP knowledge base for relevant articles"
# #         )
# #     ]

# #     memory=ConversationBufferMemory(memory_key="chat_history")

# #     agent=initialize_agent(
# #         tools,
# #         llm,
# #         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
# #         memory=memory,
# #         verbose=False
# #     )
# #     return agent

# def buildAgent():
#     # Define the endpoint
#     llm_endpoint = HuggingFaceEndpoint(
#         repo_id=CHAT_MODEL,
#         huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
#         temperature=float(TEMPERATURE),
#         max_new_tokens=512,
#     )

#     # **KEY FIX**: Wrap the endpoint in ChatHuggingFace for the agent
#     chat_model = ChatHuggingFace(llm=llm_endpoint)

#     tools = [
#         Tool(
#             name="HP_KB_Search",
#             func=search_articles, # This tool uses the RAG chain
#             description="Searches the internal HP knowledge base for relevant articles"
#         )
#     ]

#     memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#     agent = initialize_agent(
#         tools,
#         chat_model, # <-- Use the chat model
#         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#         memory=memory,
#         verbose=False,
#         handle_parsing_errors=True 
#     )
#     return agent

# agent=buildAgent()
# # print(agent.run("How can i set my laptop?"))


from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
import os, sys
from main import get_rag
# Load environment variables
CHAT_MODEL = os.environ.get("CHAT_MODEL") or "llama-3.1-8b-instant"  # Groq supports llama-3.1-8b-instant, mixtral, etc.
TEMPERATURE = float(os.environ.get("CHAT_MODEL_TEMPERATURE") or 0.2)

def small_talk_tool(query: str) -> str:
    query = query.lower().strip()
    if any(greet in query for greet in ["hi", "hello", "hey"]):
        return "Hello 👋! How can I help you today?"
    elif "thank" in query:
        return "You're welcome! 🙂 Happy to assist."
    elif "bye" in query:
        return "Goodbye 👋, have a great day!"
    else:
        return "This seems like a general query. How can I assist you further?"

def search_articles(query: str):
    rag = get_rag()
    result = rag.invoke({"input": query})
    answer = result.get("answer") or result.get("output") or str(result)
    ctx = result.get("context") or []

    # Collect HP KB sources
    hp_articles = [doc.metadata.get("source", "Unknown") for doc in ctx[:5]]

    # # If the answer is too vague or missing, try Tabuli
    # if not answer or answer.strip().lower() in ["i don't know", "not available"]:
    #     tabuli_results = tabuli_search(query)
    #     return f"{tabuli_results}\n\n(HP KB had no specific answer.)"

    # Optionally also add Tabuli results for completeness
    tabuli_results = tabuli_search(query)

    return (
        f"{answer}\n\n"
        f"Top HP KB articles:\n" + "\n".join(hp_articles) + "\n\n"
        f"Additional references from Tabuli:\n{tabuli_results}"
    )

def tabuli_search(query: str) -> str:
    """
    Calls Tabuli search API and returns top results.
    Replace the dummy implementation with the real Tabuli client/API call.
    """
    try:
        # Example: replace with actual tabuli API usage
        from tabuli import search  
        results = search(query)  # returns a list of results (dicts or strings)

        if not results:
            return "No results found from Tabuli."

        formatted = "\n".join([f"- {res}" for res in results[:5]])
        return f"Here are some results from Tabuli:\n{formatted}"
    except Exception as e:
        return f"Tabuli search failed: {str(e)}"

def buildAgent():
    # Use Groq instead of HuggingFaceHub
    llm = ChatGroq(
        model=CHAT_MODEL,
        temperature=TEMPERATURE,
    )

    tools = [
        Tool(
            name="HP_KB_Search",
            func=search_articles,
            description="Searches the internal HP knowledge base for relevant articles"
        ),Tool(
            name="SmallTalk",
            func=small_talk_tool,
            description="Handles general conversation like greetings, thanks, or casual chat"
        ),Tool(
        name="TabuliSearch",
        func=tabuli_search,
        description="Searches the Tabuli knowledge/document index for additional references"
    )
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # agent = initialize_agent(
    #     tools=tools,
    #     llm=llm,
    #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    #     memory=memory,
    #     verbose=False,
    #     agent_kwargs={
    #     "description": (
    #     "You are a helpful AI assistant. "
    #     "Use HP_KB_Search for HP-specific manuals and troubleshooting. "
    #     "If the answer seems incomplete or missing, use TabuliSearch to find additional references. "
    #     "Always provide clear troubleshooting steps and include references when available. "
    #     "Handle casual greetings or small talk politely."
    #     )
    # }
    # )
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        # --- THIS IS THE ONLY CHANGE YOU NEED TO MAKE ---
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, 
        # ---                                          ---
        memory=memory,
        verbose=True, # Set to True to see its improved reasoning!
        agent_kwargs={
            "system_message": ( # system_message is often better for conversational agents
                "You are a helpful AI assistant. "
                "Use HP_KB_Search for HP-specific manuals and troubleshooting. "
                "If the answer seems incomplete or missing, use TabuliSearch to find additional references. "
                "Always provide clear troubleshooting steps and include references when available. "
                "Handle casual greetings, thanks, or small talk politely using the SmallTalk tool."
            )
        }
    )
    return agent

agent = buildAgent()
# print(agent.run("How can i set my laptop?"))
