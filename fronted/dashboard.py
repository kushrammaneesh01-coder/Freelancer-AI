import streamlit as st
from backend.graph.workflow import workflow

st.title("AI Freelancing Automation Agency")

skills = st.text_input("Your Skills", "Python, LangChain")
run = st.button("Find Jobs")

if run:
    state = {
        "jobs": [
            {
                "title": "Build AI chatbot",
                "description": "Need LangChain expert",
                "budget": 300
            }
        ]
    }
    result = workflow.invoke(state)
    st.json(result)
