import sys
import json
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import asyncio
import websockets

# Load environment variables
load_dotenv()

# Default port setting
PORT = 3003

async def handle_websocket(websocket, path):
    async for message in websocket:
        try:
            request = json.loads(message)
            if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid JSON-RPC version"},
                    "id": request.get("id")
                }
                await websocket.send(json.dumps(response))
                continue
            
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "name": "MySQL MCP Server",
                        "version": "1.0.0",
                        "status": "initialized"
                    },
                    "id": request_id
                }
            elif method == "tools/list":
                tools = [
                    {
                        "name": "list_tables",
                        "description": "List all tables in the database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "password": {"type": "string"},
                                "database": {"type": "string"}
                            },
                            "required": ["user_id", "password"]
                        }
                    },
                    {
                        "name": "query",
                        "description": "Execute a SQL query",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "password": {"type": "string"},
                                "database": {"type": "string"},
                                "query": {"type": "string"}
                            },
                            "required": ["user_id", "password", "query"]
                        }
                    }
                ]
                response = {
                    "jsonrpc": "2.0",
                    "result": tools,
                    "id": request_id
                }
            elif method == "tools/call":
                tool = params.get("tool")
                tool_params = params.get("params", {})
                
                if tool == "list_tables":
                    response = await handle_list_tables(tool_params, request_id)
                elif tool == "query":
                    response = await handle_query(tool_params, request_id)
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": f"Unknown tool: {tool}"},
                        "id": request_id
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Unknown method: {method}"},
                    "id": request_id
                }
            
            await websocket.send(json.dumps(response))
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": request.get("id") if "request" in locals() else None
            }
            await websocket.send(json.dumps(error_response))

async def handle_list_tables(params, request_id):
    if "user_id" not in params or "password" not in params:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Missing user ID or password"},
            "id": request_id
        }
    
    db_config = {
        'user': params['user_id'],
        'password': params['password'],
        'host': 'localhost',
        'database': params.get('database', '')
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        return {
            "jsonrpc": "2.0",
            "result": {"tables": tables},
            "id": request_id
        }
    except mysql.connector.Error as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": f"Database error: {str(e)}"},
            "id": request_id
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

async def handle_query(params, request_id):
    if "user_id" not in params or "password" not in params or "query" not in params:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Missing user ID, password, or query"},
            "id": request_id
        }
    
    db_config = {
        'user': params['user_id'],
        'password': params['password'],
        'host': 'localhost',
        'database': params.get('database', '')
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(params["query"])
        results = cursor.fetchall()
        
        return {
            "jsonrpc": "2.0",
            "result": {"results": results},
            "id": request_id
        }
    except mysql.connector.Error as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": f"Database error: {str(e)}"},
            "id": request_id
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

async def run_websocket_server(port):
    try:
        async with websockets.serve(handle_websocket, "0.0.0.0", port):
            print(f"WebSocket server running on port {port}", file=sys.stderr)
            sys.stderr.flush()
            await asyncio.Future()  # Run forever
    except Exception as e:
        print(f"Error starting WebSocket server: {str(e)}", file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)

if __name__ == "__main__":
    try:
        port = PORT
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        
        # Run the WebSocket server
        asyncio.run(run_websocket_server(port))
    except Exception as e:
        print(f"Failed to run WebSocket server: {str(e)}", file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1) 