import sys
import json
import asyncio
import websockets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default port setting
PORT = int(os.getenv('PORT', '3003'))

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
                await websocket.send(json.dumps(response))
            elif method == "tools/list":
                tools = [
                    {
                        "name": "echo",
                        "description": "Echo back a message",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string", "description": "Message to echo"}
                            },
                            "required": ["message"]
                        }
                    }
                ]
                response = {
                    "jsonrpc": "2.0",
                    "result": tools,
                    "id": request_id
                }
                await websocket.send(json.dumps(response))
            elif method == "tools/call":
                tool = params.get("tool")
                tool_params = params.get("params", {})
                
                if tool == "echo":
                    message = tool_params.get("message", "")
                    response = {
                        "jsonrpc": "2.0",
                        "result": {"echo": message},
                        "id": request_id
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": f"Unknown tool: {tool}"},
                        "id": request_id
                    }
                await websocket.send(json.dumps(response))
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