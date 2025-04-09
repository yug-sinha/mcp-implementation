# MCP Implementation

This repository implements an MCP (Modular Conversational Platform) example with two servers and a client API. The servers simulate simple tools:
- **SQL Warehouse Server:** Converts plain-text instructions to SQL queries.
- **Vector Search Server:** Simulates a vector database query.

The client API forwards requests to Gemini for generating function calls and then calls the appropriate server tool via STDIO transport.

## Repository Structure

- `.env` - Environment variable definitions.
- `.gitignore` - Ignores virtual environment and env files.
- `client.py` - FastAPI application exposing the `/generate` endpoint.
- `docker-compose.yml` - Docker Compose configuration to run the application containers.
- `Dockerfile` - Dockerfile for building the application image.
- `requirements.txt` - Python package dependencies.
- `sql_server.py` - Implements the simulated SQL tool.
- `vector_server.py` - Implements the simulated vector search tool.

## Prerequisites

- Python 3.13 (or higher) with pip
- Docker and Docker Compose (if running with containers)
- A valid GEMINI_API_KEY stored in the `.env` file

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

## Running the Application

### Using Docker Compose

Run all services (SQL Server, Vector Search Server, and Client API) via Docker Compose:
```sh
docker compose up --build
```
This will start containers for:
- **SQL Server** on port `8001`
- **Vector Search Server** on port `8002`
- **Client API** on port `8080`


## API Usage

The FastAPI client exposes an endpoint to generate tool outputs.

- **POST** `/generate`  
  **Curl Command Example:**
  ```sh
  curl --location 'http://localhost:8080/generate' \
    --header 'Content-Type: application/json' \
    --data '{"instruction": "Convert the following instruction into an SQL query: select all customers with outstanding balance"}'
  ```

The API will forward the instruction to Gemini to generate a function call (`txt_to_sql` or `vector_search`) and then call the appropriate server to process the tool.

## Logging

The application uses colored logging (via [`colorlog`](venv/lib/python3.10/site-packages/colorlog/__init__.py)) for better visibility and debugging.

