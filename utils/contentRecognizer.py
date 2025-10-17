from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

def categorizationBuilder(tc,categories:list):
    # tc=data.get("ticket_content")


    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": "Explain the importance of fast language models",
    #         },{
    #             "role":"system",
    #             "content":"You are financial advisor"
    #         }
    #     ],
    #     model="openai/gpt-oss-20b",
    #     temperature=0.6,
    #     stream=False,
    # )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""This is ticket content {tc}""",
            },{
                "role":"system",
                "content":f"""You are experienced ticket categorization analyst 
                           Based on the user's ticket content 
                           you will categorize the ticket  by semantic meaning

                           Notes:
                           you will categorize from the mentioned categories by semantic meaning

                           -only return category no nuance explaination
                           for example refund

                           return only the category that is present in {categories}

                """
            }
        ],
        model=os.environ.get("CATEGORIZATION_MODEL"),
        temperature=float(os.environ.get("CATEGORIZATION_TEMPERATURE")),
        stream=False,
    )

    return chat_completion.choices[0].message.content

def satisfactionDetector(content):
    client=Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )
    chat_satisfaction=client.chat.completions.create(
        messages=[
            {
                "role":"user",
                "content":f"This is content of the ticket{content}"
            },{
                "role":"system",
                "content":f"""
                    You are Experienced Ticket Emotion detector based on the ticket content provided by the user, tell whether the user is satisfied 

                    Note : Only return True or False if the user is satisfied return True else return False
                """
            }
        ],
        model=os.environ.get("CATEGORIZATION_MODEL"),
        temperature=float(os.environ.get("CATEGORIZATION_TEMPERATURE")),
        stream=False

    )
    return chat_satisfaction.choices[0].message.content

def sentimentDetector(query):
    client=Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )
    sentiment_detector=client.chat.completions.create(messages=[
        {
                "role":"user",
                "content":f"This is content of the ticket{query}"
            },{
                "role":"system",
                "content":f"""
                    You are Experienced Ticket Emotion detector based on the ticket content provided by the user, tell the sentiment of the query
                    Note: return only the sentiment of the query that is present in the following list of sentiments [Positive, Negative,Neutral]
                """
        }
    ],model=os.environ.get("CATEGORIZATION_MODEL"),
    temperature=float(os.environ.get("CATEGORIZATION_TEMPERATURE")),
    stream=False)

    return sentiment_detector.choices[0].message.content



print(sentimentDetector("Are you Mad?"))