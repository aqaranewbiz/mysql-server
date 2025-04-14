from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from mcp import MCPServer, Tool, Resource

# Load environment variables
load_dotenv()

app = FastAPI()

# MySQL connection configuration
mysql_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', '')
}

# MCP 서버 초기화
mcp_server = MCPServer(
    name="MySQL MCP Server",
    description="MySQL 데이터베이스에 대한 쿼리 실행을 지원하는 MCP 서버",
    version="1.0.0"
)

# MySQL 쿼리 도구 정의
mysql_query_tool = Tool(
    name="mysql_query",
    description="Execute MySQL queries",
    parameters={
        "query": {
            "type": "string",
            "description": "SQL query to execute"
        }
    }
)

# MySQL 리소스 정의
mysql_resource = Resource(
    name="mysql",
    description="MySQL database connection",
    config=mysql_config
)

# 도구와 리소스를 서버에 등록
mcp_server.register_tool(mysql_query_tool)
mcp_server.register_resource(mysql_resource)

@app.get("/status")
async def get_status():
    """Return the server status and available tools"""
    return mcp_server.get_status()

@app.post("/execute")
async def execute_tool(tool_name: str, params: Dict[str, Any]):
    """Execute the requested tool"""
    try:
        result = await mcp_server.execute_tool(tool_name, params)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 