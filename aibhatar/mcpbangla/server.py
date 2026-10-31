import json
from typing import Any, Optional

class MCPPortServer:
    """Simple HTTP server handling MCP protocol requests."""
    
    def __init__(self, port: int = 6469):
        self.port = port
        self.client_url = f"http://localhost:{port}"
        
    def handle_request(self, method: str) -> tuple[dict, dict]:
        """Handle MCP protocol request."""
        import urllib.request
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            url = self.client_url.rstrip('/') + method
            if method == '/mcp/initialize':
                resp = urllib.request.urlopen(url, timeout=10)
                data = json.loads(resp.read().decode())
            elif method == '/mcp/tools':
                resp = urllib.request.urlopen(url, timeout=10)
                data = json.loads(resp.read().decode())
            else:
                raise ValueError(f"Unknown MCP method: {method}")
                
            return data, {'status': 'success'}
        except Exception as e:
            error_data = {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
            return error_data, {'status': 'error'}


def main():
    """Run the MCP server."""
    print(f"Starting MCP server on port 6469...")
    
    while True:
        try:
            import urllib.request
            request = urllib.request.Request(
                "/mcp/initialize",
                data=json.dumps({"type": "init"}).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(request, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                print(f"Initialized: {data.get('server_name', 'Unknown')}")
                
        except Exception as e:
            if hasattr(e, 'args') and len(e.args) > 0:
                print(f"Error: {str(e.args[0])}")
            else:
                print(f"Error: {e}")

if __name__ == '__main__':
    main()
