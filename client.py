# pip install google-generativeai mcp httpx python-dotenv anthropic colorlog
import asyncio
import os
import json
import logging
from colorlog import ColoredFormatter
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Setup colored logging
LOGFORMAT = "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s"
formatter = ColoredFormatter(LOGFORMAT, datefmt=None,
                             log_colors={
                                 'DEBUG':    'cyan',
                                 'INFO':     'green',
                                 'WARNING':  'yellow',
                                 'ERROR':    'red',
                                 'CRITICAL': 'red,bg_white',
                             })
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("MCPClient")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Load environment variables (GEMINI_API_KEY must be defined in .env)
load_dotenv()

# Instantiate the Gemini client using GEMINI_API_KEY
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
logger.info("Gemini client initialized.")

# Hard-coded tool definitions simulating retrieval from an MCP host.
TOOLS_DEFINITIONS = {
    "tools": [
        {
            "name": "txt_to_sql",
            "description": "Converts a text instruction into an SQL query for the warehouse.",
            "inputSchema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        },
        {
            "name": "vector_search",
            "description": "Performs a vector search in a vector database.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    ]
}

def reconstruct_tool_schema(input_schema: dict) -> dict:
    """
    Reconstruct the tool input schema into a standard JSON schema.
    """
    return {
        "type": "object",
        "properties": input_schema.get("properties", {})
    }

# Reformat tool definitions for Gemini.
gemini_tools = [
    types.Tool(
        function_declarations=[{
            "name": tool["name"],
            "description": tool["description"],
            "parameters": reconstruct_tool_schema(tool["inputSchema"])
        }]
    )
    for tool in TOOLS_DEFINITIONS["tools"]
]
logger.debug(f"Reformatted tool definitions for Gemini: {gemini_tools}")

async def connect_and_call_tool(server_script: str, tool_name: str, arguments: dict) -> dict:
    """
    Connect to an MCP server by launching the provided server script via STDIO
    and call the specified tool with the provided arguments.
    """
    logger.info(f"Launching server script '{server_script}' to call tool '{tool_name}' with arguments: {arguments}")
    params = StdioServerParameters(
        command="python3",  # Adjust to 'python' on Windows if needed.
        args=[server_script],
        env=None
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            logger.debug("Initializing MCP session...")
            await session.initialize()
            logger.debug(f"Calling tool '{tool_name}' with arguments wrapped as params.")
            # Wrap tool arguments in a dict with "params" key.
            result = await session.call_tool(tool_name, {"params": arguments})
            logger.info("Tool call completed.")
            return result

async def run():
    # Prompt user for input.
    prompt = input("Enter your instruction: ").strip()
    logger.info(f"User prompt received: {prompt}")

    logger.info("Calling Gemini to generate content...")
    response = gemini_client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            tools=gemini_tools,
        ),
    )
    
    logger.debug("Gemini response received.")
    candidate = response.candidates[0]
    first_part = candidate.content.parts[0]
    if first_part.function_call:
        function_call = first_part.function_call
        tool_name = function_call.name
        tool_args = dict(function_call.args)
        logger.info(f"Gemini generated a function call: {tool_name} with arguments: {tool_args}")
        
        # Determine which server script to launch based on the tool name.
        if tool_name == "txt_to_sql":
            server_script = "./sql_server.py"
        elif tool_name == "vector_search":
            server_script = "./vector_server.py"
        else:
            logger.error(f"Unknown tool requested by Gemini: {tool_name}")
            return
        
        result = await connect_and_call_tool(server_script, tool_name, tool_args)
        logger.info("Tool call result received. Processing output...")
        print("--- Formatted Result ---")
        try:
            result_dict = result.model_dump()
            content = result_dict.get("content")
            if content and isinstance(content, list) and len(content) > 0:
                try:
                    parsed = json.loads(content[0].get("text", ""))
                    print(json.dumps(parsed, indent=2))
                    logger.debug("Parsed JSON output from tool call successfully.")
                except json.JSONDecodeError:
                    print(content[0].get("text", ""))
                    logger.debug("Output is plain text, not JSON.")
            else:
                print(result_dict)
                logger.debug("No 'content' field found in the result.")
        except Exception as e:
            logger.error(f"Error processing the result: {e}")
            print(result)
    else:
        logger.info("No function call generated by Gemini.")
        if response.text:
            print("Model response:")
            print(response.text)

asyncio.run(run())
