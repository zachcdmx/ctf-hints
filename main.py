from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
import gradio as gr

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.8)
search = GoogleSerperAPIWrapper()

@tool
def search_tool(query: str) -> str:
    """Pass as the query argument, the name the user gave of the CTF challenge to search through relevant walkthroughs."""
    query = f"{query} walkthrough"
    res = search.run(query)
    return res

system_prompt = SystemMessage(content=[{ "type" : "text", "text": "You are a CTF expert helping users solve challenges, without giving away direct answers. Make sure to use the search tool to gather info online about the CTF in question." }])

agent = create_agent(llm, tools=[search_tool], system_prompt=system_prompt)

def hint(challenge: str = "portswigger low level logic lab") -> str:
    """Get a hint for a CTF challenge."""
    user_message = HumanMessage(content=[{ "type": "text", "text" : f"I am working on the challenge '{challenge}'. Provide a hint without giving away the answer." }])
    msgs = [user_message]
    # print(" start of event stream FUCK")
    # for event in agent.stream({ "messages": msgs }, stream_mode=["updates"]):
    #    print(" Event:", event)
    res = agent.invoke({ "messages": msgs })
    
    msg_content = []


    for message in res["messages"]:
        msg_content.append(message.content)

    return msg_content[-1]


def test_search_tool():
    result = search_tool("portswigger low level logic lab")
    print(result)
    return result


ui = gr.Interface(
    fn=hint,
    inputs=[
        gr.Textbox(label="CTF Challenge", placeholder="Enter the name of the CTF challenge..."),
    ],
    outputs=gr.Textbox(label="Hint"),
    title="CTF Challenge Hint Generator",
    description="Get hints for CTF challenges without revealing the answers."
)


test_ui = gr.Interface(
    fn=test_search_tool,
    inputs=[],
    outputs=gr.Textbox(label="Search Tool Test Result"),
    title="Test Search Tool",
    description="Test the search tool functionality."
)

if __name__ == "__main__":
    ui.launch()
    # hint()

