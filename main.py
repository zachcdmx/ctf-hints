from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
import requests

import gradio as gr

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.8)
search = GoogleSerperAPIWrapper()


@tool
def fetch_ctf_page_description(url: str) -> str:
    """Fetch the description of a CTF challenge from a given URL."""
    try:
        text = requests.get(url).text[:2000]  # Limit to first 2000 characters
        return text
    except Exception as e:
        return str(e)

@tool
def search_tool(query: str) -> str:
    """Pass as the query argument, the name the user gave of the CTF challenge to search through relevant walkthroughs."""
    query = f"{query} walkthrough"
    res = search.run(query)
    return res

system_prompt = SystemMessage(content=[{ "type" : "text", "text": "You are a CTF expert helping users solve challenges, without giving away direct answers. Use the fetch_ctf_page_description description tool to accept the url to the CTF challenge description, read the page, and based in that search for the relevant results before giving hints to the user" }])

agent = create_agent(llm, tools=[search_tool, fetch_ctf_page_description], system_prompt=system_prompt)

def hint(challenge_url: str) -> str:
    """Get a hint for a CTF challenge."""
    user_message = HumanMessage(content=[{ "type": "text", "text" : f"I am working on the challenge at the url: '{challenge_url}'. Provide a hint without giving away the answer." }])
    msgs = [user_message]
    # print(" start of event stream FUCK")
    # for event in agent.stream({ "messages": msgs }, stream_mode=["updates"]):
    #    print(" Event:", event)
    

    res = agent.invoke({ "messages": msgs })
    
    msg_content = []


    for message in res["messages"]:
        msg_content.append(message.content)

    return msg_content[-1]


ui = gr.Interface(
    fn=hint,
    inputs=[
        gr.Textbox(label="CTF URL", placeholder="Enter the URL of the CTF challenge..."),
    ],
    outputs=gr.Textbox(label="Hint"),
    title="CTF Challenge Hint Generator",
    description="Get hints for CTF challenges without revealing the answers."
)

if __name__ == "__main__":
    ui.launch()
    # hint()

