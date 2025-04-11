import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
# Smithery AI SDK import
from smithery_ai_sdk import SmitheryAI

# Load environment variables
load_dotenv()

# 기본 포트 설정
PORT = 3003

# Smithery AI 설정
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')
smithery = SmitheryAI(api_key=SMITHERY_API_KEY)

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
    
    def do_GET(self):
        if self.path == "/status":
            self._set_headers()
            status = {
                "status": "running",
                "type": "mysql",
                "tools": ["list_tables", "query"]
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self._handle_error(404, "Not found")
    
    def do_POST(self):
        if self.path == "/execute":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode())
            
            if "tool" not in request or "parameters" not in request:
                return self._handle_error(400, "Missing tool or parameters")
            
            tool = request["tool"]
            params = request["parameters"]
            
            if tool == "list_tables":
                return self.handle_list_tables(params)
            elif tool == "query":
                return self.handle_query(params)
            else:
                return self._handle_error(400, f"Unknown tool: {tool}")
    
    def handle_list_tables(self, params):
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
            self.wfile.write(json.dumps({"tables": tables}).encode())
            
        except mysql.connector.Error as e:
            return self._handle_error(500, f"Database error: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def handle_query(self, params):
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
            self.wfile.write(json.dumps({"results": results}).encode())
            
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
    
    # Smithery AI에 서버 등록
    try:
        smithery.register_server(name="MySQL MCP Server", description="A simple MySQL MCP server.", port=port)
        print("Server registered with Smithery AI.")
    except Exception as e:
        print(f"Failed to register server with Smithery AI: {str(e)}")
    
    httpd.serve_forever()

if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port) 