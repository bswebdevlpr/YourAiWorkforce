# Build workflow
from langchain import messages
from langgraph.graph import END, START, MessagesState, StateGraph

from edges import should_continue
from model import llm_call
from tools import tool_node

agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()

# Invoke
from langchain.messages import HumanMessage

messgaes = [HumanMessage(content="Add 3 and 4.")]
messgaes = agent.invoke({"messgaes": messgaes})
for m in messages["messages"]:
    m.pretty_print()
