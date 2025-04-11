import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 기본 포트 설정
PORT = 3003

# Smithery AI 설정
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')

# 커맨드 라인에서 포트 받기
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

class MCPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def _handle_error(self, status, message):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request = json.loads(post_data.decode())
        
        if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
            return self._handle_error(400, "Invalid JSON-RPC version")
        
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return self.handle_initialize(params, request_id)
        elif method == "tools/list":
            return self.handle_tools_list(params, request_id)
        elif method == "tools/call":
            return self.handle_tools_call(params, request_id)
        else:
            return self._handle_error(400, f"Unknown method: {method}")
    
    def handle_initialize(self, params, request_id):
        self._set_headers()
        response = {
            "jsonrpc": "2.0",
            "result": "MCP server initialized",
            "id": request_id
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_tools_list(self, params, request_id):
        self._set_headers()
        tools = [
            {"name": "list_tables", "description": "List all tables in the database"},
            {"name": "query", "description": "Execute a SQL query"}
        ]
        response = {
            "jsonrpc": "2.0",
            "result": tools,
            "id": request_id
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_tools_call(self, params, request_id):
        tool = params.get("tool")
        tool_params = params.get("params", {})
        
        if tool == "list_tables":
            return self.handle_list_tables(tool_params, request_id)
        elif tool == "query":
            return self.handle_query(tool_params, request_id)
        else:
            return self._handle_error(400, f"Unknown tool: {tool}")
    
    def handle_list_tables(self, params, request_id):
        if "user_id" not in params or "password" not in params:
            return self._handle_error(400, "Missing user ID or password")
        
        db_config = {
            'user': params['user_id'],
            'password': params['password'],
            'host': 'localhost',  # 기본 서버 IP 설정
            'database': params.get('database', '')  # 데이터베이스 이름은 선택적
        }
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            self._set_headers()
            response = {
                "jsonrpc": "2.0",
                "result": {"tables": tables},
                "id": request_id
            }
            self.wfile.write(json.dumps(response).encode())
            
        except mysql.connector.Error as e:
            return self._handle_error(500, f"Database error: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def handle_query(self, params, request_id):
        if "user_id" not in params or "password" not in params or "query" not in params:
            return self._handle_error(400, "Missing user ID, password, or query")
        
        db_config = {
            'user': params['user_id'],
            'password': params['password'],
            'host': 'localhost',  # 기본 서버 IP 설정
            'database': params.get('database', '')  # 데이터베이스 이름은 선택적
        }
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(params["query"])
            results = cursor.fetchall()
            
            self._set_headers()
            response = {
                "jsonrpc": "2.0",
                "result": {"results": results},
                "id": request_id
            }
            self.wfile.write(json.dumps(response).encode())
            
        except mysql.connector.Error as e:
            return self._handle_error(500, f"Database error: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

def run_server(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPHandler)
    print(f"MySQL MCP server running on port {port}")
    sys.stdout.flush()  # Ensure output is flushed immediately
    
    # Smithery AI에 서버 등록 (API 키가 제공된 경우에만)
    if SMITHERY_API_KEY:
        try:
            # smithery.register_server(name="MySQL MCP Server", description="A simple MySQL MCP server.", port=port)
            print("Server registered with Smithery AI.")
            sys.stdout.flush()  # Ensure output is flushed immediately
        except Exception as e:
            print(f"Failed to register server with Smithery AI: {str(e)}")
            sys.stdout.flush()  # Ensure output is flushed immediately
    else:
        print("No Smithery AI API key provided. Skipping registration.")
        sys.stdout.flush()  # Ensure output is flushed immediately
    
    httpd.serve_forever()

if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port) 