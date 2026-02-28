from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

def proposal_writer(state):
    for job in state["jobs"]:
        prompt = f"""
        Write a professional Upwork proposal for:
        {job['title']}
        Description: {job['description']}
        """
        job["proposal"] = llm.predict(prompt)
    return state
