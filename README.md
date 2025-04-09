# MCP Implementation

This repository implements an MCP (Model Context Protocol) example with two servers and a client API. The servers simulate simple tools:
- **SQL Warehouse Server:** Converts plain-text instructions to SQL queries.
- **Vector Search Server:** Simulates a vector database query.

The client API forwards requests to Gemini for generating function calls and then calls the appropriate server tool via STDIO transport. The FastAPI client exposes a `/generate` HTTP endpoint so you can hit it with curl commands. All logs are shown with color for better visibility.

---

## What is Model Context Protocol (MCP)?

Model Context Protocol (MCP) is a standardized communication framework designed to connect large language models (LLMs) with external tools, services, or data sources. It provides a consistent interface for listing available tools and invoking them with specific parameters.

**Key Concepts:**
- **Resources:** File-like data or API responses available for consumption by clients.
- **Tools:** Functions or services that perform specific tasks (e.g., converting text to SQL or querying a vector database).
- **Prompts:** Pre-defined templates or instructions to guide users in accomplishing tasks.

By using MCP, developers can build modular systems where an LLM (like those from Gemini or Anthropic) dynamically determines which tool to invoke and communicates with the respective server hosting that tool. This approach allows for a flexible and scalable system that can integrate multiple tools seamlessly.

---

## How We Implemented MCP with Gemini

In this project, we integrated the MCP servers with Gemini as follows:

1. **MCP Servers:**
   - **SQL Warehouse Server (`sql_server.py`):**  
     Implements a tool named `txt_to_sql` which simulates converting a natural language instruction into an SQL query for a warehouse.
   - **Vector Search Server (`vector_server.py`):**  
     Implements a tool named `vector_search` that simulates querying a vector database for similar documents.  
     
   Both servers use the FastMCP Python SDK with STDIO transport and include logging (with colored output) as well as a heartbeat task (in our previous versions, you can add such tasks here as needed).

2. **Client API (client.py):**
   - **Gemini Integration:**  
     The client uses Google Generative AI (Gemini) by sending the user’s instruction and a list of available tool definitions to Gemini. Gemini returns a function call (e.g., `txt_to_sql` or `vector_search`) based on the natural language prompt.
   - **MCP Invocation:**  
     Depending on the function call produced by Gemini, the client launches the respective MCP server script (either `sql_server.py` or `vector_server.py`) via STDIO transport using the MCP client connection logic.
   - **FastAPI Endpoint:**  
     The client exposes a `/generate` endpoint that accepts a JSON payload. When you send a POST request with an instruction, the API calls Gemini, chooses the appropriate tool, invokes the corresponding MCP server, and returns the tool’s output.
   - **Logging & Heartbeat:**  
     The FastAPI app logs a heartbeat every 5 seconds to indicate that it is running continuously.

3. **Docker Deployment:**
   - We provide a **Dockerfile** that installs all dependencies on an Alpine-based Python image.
   - The **docker-compose.yml** file orchestrates three services:
     - **SQL Server** mapped to port 8001.
     - **Vector Search Server** mapped to port 8002.
     - **Client API** (FastAPI) mapped to port 8080.
   - This setup allows you to run all components concurrently and see all colored logs in one terminal.

---

## Repository Structure

- `.env` - Environment variable definitions.
- `.gitignore` - Ignores virtual environment and env files.
- `client.py` - FastAPI application exposing the `/generate` endpoint.
- `docker-compose.yml` - Docker Compose configuration to run the application containers.
- `Dockerfile` - Dockerfile for building the application image.
- `requirements.txt` - Python package dependencies.
- `sql_server.py` - Implements the simulated SQL tool.
- `vector_server.py` - Implements the simulated vector search tool.

---

## Prerequisites

- Python 3.13 (or higher) with pip
- Docker and Docker Compose (Docker Compose V2 is recommended; use `docker compose` commands)
- A valid GEMINI_API_KEY stored in the `.env` file

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd mcp-implementation
   ```

2. **Create a virtual environment (optional) and install dependencies:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

---

## Running the Application

### Using Docker Compose

Run all services (SQL Server, Vector Search Server, and Client API) via Docker Compose:

```sh
docker compose up --build
```

This starts three containers:
- **SQL Server** on port `8001`
- **Vector Search Server** on port `8002`
- **Client API** on port `8080`

All logs are streamed to your terminal.

---

## API Usage

The FastAPI client exposes an endpoint to generate tool outputs.

- **POST** `/generate`  
  **Curl Command Example:**
  ```sh
  curl --location 'http://localhost:8080/generate' \
       --header 'Content-Type: application/json' \
       --data '{"instruction": "Convert the following instruction into an SQL query: select all customers with outstanding balance"}'
  ```

The API forwards the instruction to Gemini, which generates a function call. Based on the function call, the client launches the appropriate MCP server (SQL or vector) and returns the output.

---

## Logging

- **Client API:**  
  The FastAPI app logs every 5 seconds a heartbeat to show it is running. It also logs every key step (e.g., receiving the instruction, calling Gemini, and processing the tool output).

- **MCP Servers:**  
  Both servers log when they start, when they receive tool calls, and the outputs they generate, using colored logging via `colorlog`.

All logs are visible concurrently when running with Docker Compose.

---

## License

This project is licensed under the MIT License.
```

---

This README provides a clear breakdown of what MCP is, how we’ve integrated it using Gemini in our implementation, and the overall working of the code. It also includes the Docker build and run commands for deploying the application with continuous logging and live API access via curl.