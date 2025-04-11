import asyncio
import json
import sys
import os
import websockets
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

# 날짜/시간 처리를 위한A JSON 인코더
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

# MySQL configuration from environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', '')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', '')

# Create MySQL connection
def get_connection(database=None):
    try:
        db_config = {
            'host': MYSQL_HOST,
            'port': MYSQL_PORT,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD
        }
        
        if database:
            db_config['database'] = database
        elif MYSQL_DATABASE:
            db_config['database'] = MYSQL_DATABASE
            
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error connecting to MySQL: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise

async def handle_message(websocket):
    async for message in websocket:
        try:
            # Parse the JSON-RPC message
            request = json.loads(message)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Handle different methods
            if method == "initialize":
                # Test MySQL connection during initialization
                connection_status = "success"
                error_message = None
                
                try:
                    conn = get_connection()
                    conn.close()
                except Error as e:
                    connection_status = "failed"
                    error_message = str(e)
                
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "name": "MySQL MCP Server",
                        "version": "1.0.0",
                        "status": "initialized",
                        "mysql_connection": connection_status,
                        "mysql_error": error_message,
                        "config": {
                            "mysql_host": MYSQL_HOST,
                            "mysql_port": MYSQL_PORT
                        }
                    },
                    "id": request_id
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "result": [
                        {
                            "name": "mysql_query",
                            "description": "Execute a SQL query on MySQL database",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string", 
                                        "description": "SQL query to execute"
                                    },
                                    "db_config": {
                                        "type": "object", 
                                        "description": "Optional database configuration",
                                        "properties": {
                                            "host": {"type": "string", "description": "Database host"},
                                            "port": {"type": "integer", "description": "Database port"},
                                            "user": {"type": "string", "description": "Database user"},
                                            "password": {"type": "string", "description": "Database password"},
                                            "database": {"type": "string", "description": "Database name"}
                                        }
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    ],
                    "id": request_id
                }
            elif method == "tools/call":
                tool = params.get("tool")
                tool_params = params.get("params", {})
                
                if tool == "mysql_query":
                    query = tool_params.get("query")
                    db_config = tool_params.get("db_config", {})
                    
                    if not query:
                        response = {
                            "jsonrpc": "2.0",
                            "error": {"code": -32602, "message": "Missing query parameter"},
                            "id": request_id
                        }
                    else:
                        try:
                            # Use provided db_config if available, otherwise use environment variables
                            if db_config:
                                conn = mysql.connector.connect(**db_config)
                            else:
                                conn = get_connection()
                                
                            cursor = conn.cursor(dictionary=True)
                            cursor.execute(query)
                            
                            try:
                                # SELECT 쿼리 결과 가져오기
                                results = cursor.fetchall()
                                # 결과 리스트가 비어있으면 다른 유형의 쿼리로 간주
                                if not results:
                                    conn.commit()
                                    results = {"affectedRows": cursor.rowcount}
                            except Error:
                                # SELECT가 아닌 쿼리 (INSERT, UPDATE 등) 처리
                                conn.commit()
                                results = {"affectedRows": cursor.rowcount}
                            
                            cursor.close()
                            conn.close()
                            
                            response = {
                                "jsonrpc": "2.0",
                                "result": {"results": results},
                                "id": request_id
                            }
                        except Error as e:
                            response = {
                                "jsonrpc": "2.0",
                                "error": {"code": -32000, "message": f"Database error: {str(e)}"},
                                "id": request_id
                            }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": f"Unknown tool: {tool}"},
                        "id": request_id
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id
                }
            
            # Send the response
            await websocket.send(json.dumps(response, cls=DateTimeEncoder))
        except Exception as e:
            # Handle errors
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request_id if "request_id" in locals() else None
            }
            await websocket.send(json.dumps(error_response, cls=DateTimeEncoder))

async def main():
    # Start the WebSocket server
    port = 3003
    print(f"Starting MySQL MCP WebSocket server on port {port}", file=sys.stderr)
    print(f"MySQL configuration: {MYSQL_HOST}:{MYSQL_PORT}", file=sys.stderr)
    sys.stderr.flush()
    
    async with websockets.serve(handle_message, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main()) 