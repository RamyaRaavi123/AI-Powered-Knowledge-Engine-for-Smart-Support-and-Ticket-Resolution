import streamlit as st
import plotly.express as px
import time,datetime
import pandas as pd
import os,requests
from agent import agent  
from main import system,get_rag  
from utils.contentRecognizer import categorizationBuilder,satisfactionDetector,sentimentDetector
from utils.sheets_utils import insertRecord,updateTicketStatusAndSatisfaction,get_data
from utils.validation import validate_model

rag=get_rag()
st.set_page_config(page_title="AI Customer Support System", layout="wide")

import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


# ---------- INITIALIZATION ----------
st.set_page_config(page_title="AI Agent", layout="wide")
if "agent" not in st.session_state:
    st.session_state.agent = get_rag()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ticket_id" not in st.session_state:
    st.session_state.ticket_id = int(time.time())  

if "count" not in st.session_state:
    st.session_state.count=0

if "user_name" not in st.session_state:
    st.session_state.user_name=""

personal_dashboard=False

menu = st.sidebar.selectbox("Navigation", ["Home", "Validation Dashboard"])

def personalDashboard():
    st.write("Hello")

# ----------------- SIDEBAR -----------------
st.sidebar.header("📊 Statistics")
df=get_data()
if not df.empty:
    st.sidebar.metric("Total tickets",len(df))
    st.sidebar.metric("Tickets Today", (pd.to_datetime(df["ticket_timestamp"], errors="coerce").dt.date == pd.to_datetime("today").date()).sum())
    st.sidebar.metric("Resolution Rate",f'{(df["ticket_satisfied"].eq("TRUE").mean()*100):.1f}%')
st.sidebar.markdown("---")
if st.sidebar.button("📈   Personal Dashboard"):
    personal_dashboard=True

# st.sidebar.header("⚙️ Settings")
# autosave = st.sidebar.checkbox("Autosave tickets to Excel", value=True)
# excel_file = st.sidebar.text_input("Excel file path", "tickets.xlsx")
# google_sheet_id = st.sidebar.text_input("Google Sheet ID", "")

st.sidebar.markdown("---")
st.sidebar.caption("AI Powered Smart Query Resolution & Ticketing")

# ----------------- MAIN LAYOUT -----------------
st.title("🤖 AI Powered Knowledge Engine for Smart Support and Ticket Resolution")

if "user_email" not in st.session_state:
        with st.form("chat_form"):
            email = st.text_input("Customer Email", placeholder="customer@example.com")
            submitted = st.form_submit_button("🚀 Submit")
        if submitted:
            st.session_state.user_email = email
            st.success(f"Hello {st.session_state.user_email}")
if menu=="Home":

    tab1, tab2, tab3 = st.tabs(["📋 Ticket Resolution (RAG)", "💬 Agent Chat","📊 Analytics Dashboard"])

    # ----------------- TAB 1: RAG Ticket Resolution -----------------
    with tab1:
        st.subheader("Customer Query Resolution")

        with st.form("ticket_form"):
            # email = st.text_input("Customer Email", placeholder="customer@example.com")
            # name = st.text_input("Customer Name", placeholder="Enter customer name")
            # issue_summary = st.text_input("Issue Summary", placeholder="Short description of issue")
            issue_details = st.text_area("Detailed Issue Description", placeholder="Describe the problem in detail")

            submitted = st.form_submit_button("🚀 Submit & Get Resolution")

        if submitted and issue_details.strip():
            with st.spinner("Fetching RAG response..."):
                try:
                    answer, sources = system(issue_details)
                    st.markdown("### ✅ AI Suggested Resolution")
                    st.success(answer)

                    if sources:
                        st.markdown("### 📚 Sources")
                        st.info(sources)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")

    # ----------------- TAB 2: Agent Chat -----------------
    
    with tab2:
        st.header("Chat with AI Agent")

        # Email setup
        
        # New Chat button
        if st.button("🆕 New Chat"):
            st.session_state.count = 0
            st.session_state.ticket_id = int(time.time())
            st.session_state.chat_history = []

        # Input box always at bottom
        user_input = st.chat_input("Type your message...")

        if user_input:
            with st.spinner("Thinking..."):
                # Save user message first
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # Call agent
                context = "\n".join([f'{m["role"]}: {m["content"]}' for m in st.session_state.chat_history])
                result = st.session_state.agent.invoke({"input": user_input})
                answer = result.get("answer") or result.get("output") or str(result)

                # Save agent reply
                st.session_state.chat_history.append({"role": "assistant", "content": answer.strip()})

                # --- your ticket logic ---
                categories = [
                    "Getting Started","Troubleshooting","Connectivity",
                    "Power Management","Hardware","Support","Software","Security"
                ]

                if st.session_state.count == 0:
                    ticket_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ticket_sentiment = sentimentDetector(user_input)
                    ticket_cat = categorizationBuilder(user_input, categories)
                    ticket_satisfaction = satisfactionDetector(user_input)
                    ticket_by = st.session_state.user_email
                    ticket_status = "process"

                    insertRecord([
                        st.session_state.ticket_id,user_input,ticket_cat,
                        ticket_timestamp,ticket_by,ticket_status,
                        ticket_sentiment,ticket_satisfaction,answer
                    ])

                ticket_satisfaction = satisfactionDetector(user_input)
                if ticket_satisfaction == "True":
                    ticket_status = "Completed"
                    updateTicketStatusAndSatisfaction(st.session_state.ticket_id, ticket_status, "True")

                st.session_state.count += 1

        # ✅ Render chat history at the very end (after appending new msgs)
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

    with tab3:
        st.title("📊 Ticket Analytics Dashboard")

        df = get_data()
        if df.empty:
            st.warning("No ticket data available.")
        else:
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tickets", len(df))
            with col2:
                st.metric("Completed Tickets", (df["ticket_status"]=="Completed").sum())
            with col3:
                st.metric("Avg. Satisfaction", f'{(df["ticket_satisfied"].eq("TRUE").mean()*100):.1f}%')
            with col4:
                st.metric("Top Category", df["ticket_cat"].mode()[0] if not df.empty else "N/A")

            # 1. Category Frequency
            st.subheader("Category Frequency")
            cat_counts = df["ticket_cat"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig1 = px.bar(cat_counts, x="Category", y="Count", color="Count", title="Tickets per Category")
            st.plotly_chart(fig1, use_container_width=True)

            # 2. Satisfaction Analysis
            st.subheader("Satisfaction by Category")
            sat_summary = (
                df.groupby("ticket_cat")["ticket_satisfied"]
                .value_counts(normalize=True)
                .unstack()
                .fillna(0) * 100
            )

            # Handle TRUE/FALSE properly
            sat_summary = sat_summary.rename(columns={"TRUE": "Satisfied", "FALSE": "Not Satisfied"})

            fig2 = px.bar(sat_summary, barmode="stack", title="Satisfaction Breakdown (%)")
            st.plotly_chart(fig2, use_container_width=True)

            # 3. Low Coverage Areas
            st.subheader("⚠️ Low Coverage Categories (Satisfaction < 50%)")
            
            if "Satisfied" in sat_summary.columns:
                low_cov = sat_summary[["Not Satisfied", "Satisfied"]]
                low_cov = low_cov[low_cov["Satisfied"] < 50].sort_values("Satisfied")
                
                st.dataframe(low_cov)
                
                # Send Slack notification if there are low coverage categories
                if not low_cov.empty:
                    message_text = "*<D09HRB4B5FH>⚠️ Low Coverage Categories (<50% Satisfaction)*\n" + low_cov.to_string()
                    payload = {"text": message_text}
                    requests.post(os.environ.get("SLACK_WEBHOOK_URL"), json=payload)
            else:
                st.info("No satisfaction data available yet.")

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

