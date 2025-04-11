[![smithery badge](https://smithery.ai/badge/@aqaranewbiz/mysql-server)](https://smithery.ai/server/@aqaranewbiz/mysql-server)
# MySQL MCP Server

This is a simple MySQL MCP server that allows users to list tables and execute queries on a MySQL database. The server is designed to be deployed on Smithery AI and uses the Smithery AI SDK for server registration and management.

## Features
- List tables in a MySQL database
- Execute SQL queries
- Integrated with Smithery AI for easy deployment and management

## Requirements
- Python 3.9 or later
- MySQL database
- Smithery AI account and API key

## Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MCP_Server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   Create a `.env` file in the root directory and add your Smithery AI API key:
   ```
   SMITHERY_API_KEY=your_smithery_api_key
   ```

## Usage
1. **Run the server**:
   ```bash
   python mcp_server.py
   ```
   The server will start on port 3003 by default.

2. **Access the server**:
   - **List Tables**: Send a POST request to `/execute` with the tool set to `list_tables` and provide `user_id` and `password`.
   - **Execute Query**: Send a POST request to `/execute` with the tool set to `query`, and provide `user_id`, `password`, and `query`.

## Deployment on Smithery AI
1. **Upload to GitHub**: Push your code to a GitHub repository.
2. **Add Server on Smithery AI**: Use the GitHub repository URL to add the server on Smithery AI.

## License
This project is licensed under the MIT License. 