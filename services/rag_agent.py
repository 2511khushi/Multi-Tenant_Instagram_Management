from test import OPENAI_API_KEY
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# LLM configuration
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=OPENAI_API_KEY
)

# Prompt for general RAG assistant
prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are an assistant for content marketing teams managing Instagram.

You can:
- Ingest comment-reply pairs, documents, and post captions
- Generate engaging Instagram captions based on an image
- Generate high-quality replies to comments
- Recommend actions based on past insights

Answer the following query conversationally and call any tools when needed:

Question: {question}
""".strip()
)

parser = StrOutputParser()

# Per-account chat memory
user_histories = {}

# Entry function (same pattern as your Instagram one)
async def process_rag_question(question: str, account_id: str):
    try:
        if account_id not in user_histories:
            user_histories[account_id] = [
                SystemMessage(content="You are a RAG-powered assistant for Instagram content and community teams.")
            ]
        history = user_histories[account_id]

        # Connect to MCP server (rag tools)
        client = MultiServerMCPClient({
            "rag": {
                "url": "http://localhost:8000/sse", 
                "transport": "sse"
            }
        })

        tools = await client.get_tools()
        agent = create_react_agent(llm, tools)

        formatted_prompt = (await prompt.ainvoke({"question": question})).text

        session_messages = history + [
            HumanMessage(content=f"(Account ID: {account_id})\n{formatted_prompt}")
        ]

        final_response = ""

        async for chunk in agent.astream({"messages": session_messages}):
            if "agent" in chunk and "messages" in chunk["agent"]:
                for message in chunk["agent"]["messages"]:
                    if isinstance(message, AIMessage):
                        parsed_output = parser.parse(message.content)
                        clean_response = parsed_output.strip().replace("\n\n", "\n").replace("**", "")
                        final_response += clean_response

                        # Update conversation history
                        history.append(HumanMessage(content=question))
                        history.append(AIMessage(content=clean_response))

        return {"response": final_response.strip() or "No meaningful response generated."}

    except Exception as e:
        return {"error": str(e)}
