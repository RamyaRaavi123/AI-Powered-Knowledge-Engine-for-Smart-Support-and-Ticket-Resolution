from groq import Groq
from dotenv import load_dotenv
from utils.sheets_utils import sheet
import os

load_dotenv()

def isTokenRepeated(token):
    sheet1 = sheet()
    tokens = sheet1.col_values(2)
    tokens.pop(0)  # remove header row

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON responder. "
                    "If the given token exists or is similar, reply ONLY as: {\"match\": true, \"index\": <number>} "
                    "Else reply ONLY as: {\"match\": false, \"index\": -1}"
                )
            },
            {
                "role": "user",
                "content": f"Check if token '{token}' is similar to any of {tokens}."
            }
        ],
        model="openai/gpt-oss-20b",
        temperature=0.0,  
        stream=False,
    )

    mssg = chat_completion.choices[0].message.content.strip()
    # print("🔎 Raw model response:", mssg)

    try:
        import json
        result = json.loads(mssg)
    except Exception:
        print("⚠️ Model did not return JSON, falling back to string split")
        parts = mssg.split(",")
        result = {"match": parts[0].strip().lower() == "true", "index": int(parts[1])}

    if result["match"]:
        retToken = sheet1.row_values(result["index"] + 2)
        print("\n✅ A similar question has been asked previously!")
        print("Question Raised:", retToken[1])
        print("Date & Time:", retToken[3], "Asked by:", retToken[4])
    else:
        print("\n❌ No similar question found.")
