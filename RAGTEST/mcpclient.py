import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_API_KEY = os.getenv("AVIATION_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        }
    }

)

tavily_search_tool = None

async def main():
    global tavily_search_tool
    print("Starting the MCP Client...")
    tools = await client.get_tools()
    #print("Available tools:", tools)
    for tool in tools:
        print(f"Tool Name: {tool.name}")

    tavily_search_tool = next(tool for tool in tools if tool.name == "tavily_search")
    # print("Tavily Search Tool:", tavily_search_tool)

async def search_any(query: str):
    response = await tavily_search_tool.ainvoke({"query": query})
    print(response)

if __name__ == "__main__":
    asyncio.run(main())    
    asyncio.run(search_any("Best places to visit in North Bengal in December?"))
