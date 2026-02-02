from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
import typer

app = typer.Typer()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.8)
search = GoogleSerperAPIWrapper()

@tool
def search_tool(query: str) -> str:
    """Use this tool to search for information about CTF challenges."""
    search.run(query)

system_prompt = SystemMessage(content=[{ "type" : "text", "text": "You are a CTF expert helping users solve challenges, without giving away direct answers." }])

agent = create_agent(llm, tools=[search_tool], system_prompt=system_prompt)

@app.command()
def hint(challenge: str, question: str = None):
    """Get a hint for a CTF challenge."""
    user_message = HumanMessage(content=[{ "type": "text", "text" : f"I am working on the challenge '{challenge}'. Provide a hint without giving away the answer." }])
    specific_question = HumanMessage(content=[{ "type": "text", "text": f"My specific question is: {question}" }])
    msgs = [user_message]
    
    if(question):
        msgs.append(specific_question)

    response = agent.invoke({ "messages": msgs })
    print(response)


if __name__ == "__main__":
    app()
