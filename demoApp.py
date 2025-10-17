import streamlit as st
from main import main, system ,time
import nest_asyncio
import asyncio
import pandas as pd
from utils.validation import validate_model
from agent import buildAgent
nest_asyncio.apply()

st.title("AI Powered Knowledge Engine for Smart Support and Ticket-Resolution")

menu = st.sidebar.selectbox("Navigation", ["Ask Query", "Validation Dashboard"])
from langchain_groq import ChatGroq
import os

# Simple helper to classify feedback semantically
def classify_feedback(feedback: str) -> str:
    """Return 'resolved' or 'unresolved' based on semantic meaning."""
    llm = ChatGroq(model=os.environ.get("AGENT_MODEL"))

    prompt = f"""
    The user gave this feedback: "{feedback}".
    Decide if the issue is resolved or unresolved.
    Answer with only one word: Resolved or Unresolved.
    """
    result = llm.invoke(prompt)
    return result.content.strip().lower()

if menu == "Ask Query":
    st.header("💬 Ask Your Question")
    agent = buildAgent()

    if "conversation" not in st.session_state:
        st.session_state.conversation = []
        st.session_state.last_answer = None
        st.session_state.awaiting_feedback = False

    question = st.text_input("Enter your question:")

    if st.button("Ask"):
        answer = agent.invoke({"input":question})
        answer_text = answer["output"] if isinstance(answer, dict) else str(answer)

        st.session_state.last_answer = answer_text
        st.session_state.conversation.append(("User", question))
        st.session_state.conversation.append(("Agent", answer_text))
        st.session_state.awaiting_feedback = True

    # Display conversation
    for speaker, msg in st.session_state.conversation:
        st.write(f"**{speaker}:** {msg}")

    if st.session_state.awaiting_feedback and st.session_state.last_answer:
        feedback = st.text_input("Your response (e.g., 'wonderful', 'not clear'):")

        if st.button("Send Feedback") and feedback:
            resolution = classify_feedback(feedback)

            if resolution == "resolved":
                st.success("🎉 Conversation resolved. Thank you!")
                st.session_state.awaiting_feedback = False
            else:
                st.warning("Fetching more related content...")
                refinement_prompt = f"The user was not satisfied. Provide more detailed and related content to: {question}"

                improved_answer = agent.invoke(refinement_prompt)
                improved_text = improved_answer["output"] if isinstance(improved_answer, dict) else str(improved_answer)

                st.session_state.conversation.append(("Agent (Refined)", improved_text))
                st.session_state.last_answer = improved_text
                st.session_state.awaiting_feedback = True

elif menu == "Validation Dashboard":
    st.header("📊 Ticket Classification Validation")

    if st.button("Run Validation"):
        df, acc, prec, rec, f1, report = validate_model()

        df = pd.read_csv("./docs/ticket_validation_results.csv")

        st.write("### ✅ Updated Predictions")
        st.dataframe(df)

        metrics_dict = {
            "Metric": ["Accuracy", "Precision",],
            "Value": [acc*100, prec*100,]
        }
        metrics_df = pd.DataFrame(metrics_dict)
        st.write("### 📈 Evaluation Metrics")
        st.table(metrics_df)
        # st.text(report)

# latest_iteration = st.empty()
# bar = st.progress(0)

# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)

# '...and now we\'re done!'